"""覆盖失效上游、过滤漏网和失败后不发布等回归场景；不执行下载的 JS。"""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import yaml

import sync


class FilterTests(unittest.TestCase):
    def test_grouped_bilibili_domains_are_removed(self):
        patterns = sync.compile_filters({"apps": {"patterns": ["bilibili|biliapi"]}})["apps"]
        content = r"""#!name=bilibili 单独维护
[URL Rewrite]
^https:\/\/api\.(bilibili|biliapi)\.(com|net)\/x\/ad - reject
^https:\/\/api\.example\.com\/ad - reject
"""
        filtered, removed = sync.apply_filter(content, patterns)
        self.assertEqual(removed, 1)
        self.assertNotIn("(bilibili|biliapi)", filtered)
        self.assertIn("#!name=bilibili 单独维护", filtered)
        self.assertIn(r"api\.example\.com", filtered)

    def test_filter_regex_keeps_literal_dots(self):
        patterns = sync.compile_filters({"app": {"patterns": [r"example\.com"]}})["app"]
        self.assertTrue(sync.line_match(r"api\.example\.com", patterns))
        self.assertFalse(sync.line_match("api.exampleXcom", patterns))

    def test_first_mitm_domain_removed_preserves_assignment_and_append(self):
        patterns = sync.compile_filters({"app": {"patterns": ["bilibili"]}})["app"]
        filtered, removed = sync.apply_filter(
            "[MITM]\nhostname = %APPEND% api.bilibili.com, api.example.com\n", patterns
        )
        self.assertEqual(filtered, "[MITM]\nhostname = %APPEND% api.example.com\n")
        self.assertEqual(removed, 1)

    def test_plain_mitm_assignment_is_preserved(self):
        patterns = sync.compile_filters({"app": {"patterns": ["bilibili"]}})["app"]
        filtered, _ = sync.apply_filter(
            "[MITM]\nhostname=api.bilibili.com, api.example.com\n", patterns
        )
        self.assertIn("hostname = api.example.com", filtered)
        self.assertNotIn("%APPEND%", filtered)

    def test_all_filtered_mitm_domains_leave_no_broken_assignment(self):
        patterns = sync.compile_filters({"app": {"patterns": ["bilibili"]}})["app"]
        filtered, _ = sync.apply_filter(
            "[MITM]\nhostname = %APPEND% api.bilibili.com\nh2 = true\n", patterns
        )
        self.assertNotIn("hostname", filtered)
        self.assertIn("h2 = true", filtered)


class PayloadTests(unittest.TestCase):
    def test_two_field_rejects_become_native_syntax_without_changing_maps_or_comments(self):
        content = '[URL Rewrite]\n^https://example.com/ad reject-200\n^https://example.com/list - reject-dict\n# ^https://example.com/disabled reject\n[Map Local]\n^https://example.com/m data-type=text data="{}"\n'
        result = sync.normalize_shadowrocket_rewrites(content)
        self.assertIn('^https://example.com/ad - reject-200', result)
        self.assertIn('^https://example.com/list - reject-dict', result)
        self.assertNotIn('- -', result)
        self.assertIn('# ^https://example.com/disabled reject', result)
        self.assertIn('data-type=text data="{}"', result)

    def test_invalid_javascript_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "语法"):
            sync.validate_payload(b'const message = "broken;', "script", "url")

    def test_html_with_http_200_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTML"):
            sync.validate_payload(b"<!-- redirected -->\n<!DOCTYPE html><html>homepage</html>", "script", "url")

    def test_empty_script_is_rejected(self):
        with self.assertRaises(ValueError):
            sync.validate_payload(b" \n", "script", "url")

    def test_unresolved_module_arguments_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "参数"):
            sync.validate_payload(b'[Script]\na = argument="{{{captionLang}}}"', "module", "url")

    def test_missing_script_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "script-path"):
            sync.collect_script_urls("[Script]\na = type=http-response,pattern=example\n")


class ArgumentTests(unittest.TestCase):
    def test_sparkle_template_becomes_parseable_json_without_losing_script_settings(self):
        content = '#!arguments=logLevel:"error"\n[Script]\nbilibili.request = type=http-request, script-path=https://example.com/a.js, requires-body=true, argument="[{purifyComment}, {{{logLevel}}}]"\n'
        settings = {"logLevel": "error", "purifyComment": True, "sponsorBlock": False}
        result = sync.configure_script_arguments(content, {"bilibili.request": settings})
        self.assertNotIn("{{{", result)
        self.assertNotIn("#!arguments", result)
        self.assertIn("requires-body=true", result)
        value = result.split('argument="', 1)[1].rstrip().removesuffix('"')
        self.assertEqual(json.loads(value), settings)

    def test_missing_configured_script_requires_manual_update(self):
        with self.assertRaisesRegex(ValueError, "缺少"):
            sync.configure_script_arguments("[Rule]\n", {"removed-name": {}})

    def test_duplicate_names_keep_both_different_endpoints(self):
        content = "[Script]\n淘宝 = type=http-response,pattern=splash,script-path=https://example.com/a.js\n淘宝 = type=http-response,pattern=poplayer,script-path=https://example.com/a.js\n"
        result = sync.unique_script_names(content, "Taobao")
        self.assertIn("淘宝 = type=http-response,pattern=splash", result)
        self.assertIn("Taobao.001 = type=http-response,pattern=poplayer", result)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.modules = self.root / "modules"
        self.scripts = self.root / "scripts"
        self.config = self.root / "upstream.yml"
        self.modules.mkdir()
        self.scripts.mkdir()
        self.paths = patch.multiple(
            sync, ROOT=self.root, OUTPUT_DIR=self.modules,
            SCRIPTS_DIR=self.scripts, CONFIG_PATH=self.config,
        )
        self.paths.start()
        self.addCleanup(self.paths.stop)
        self.old_module = b"#!name=previous\n[Rule]\nDOMAIN,example.com,REJECT\n"
        (self.modules / "Adblock.sgmodule").write_bytes(self.old_module)
        (self.modules / "Adblock.module").write_bytes(self.old_module)
        (self.scripts / "ad.js").write_bytes(b"previous-script")

    def run_main(self, cfg, fetcher):
        self.config.write_text(yaml.safe_dump(cfg), encoding="utf-8")
        with patch.object(sync, "fetch", side_effect=fetcher), redirect_stderr(StringIO()), redirect_stdout(StringIO()):
            return sync.main()

    def assert_previous_files(self):
        self.assertEqual((self.modules / "Adblock.sgmodule").read_bytes(), self.old_module)
        self.assertEqual((self.modules / "Adblock.module").read_bytes(), self.old_module)
        self.assertEqual((self.scripts / "ad.js").read_bytes(), b"previous-script")

    def test_upstream_404_retains_all_previous_files(self):
        cfg = {
            "scripts": [{"name": "ad.js", "url": "good"}],
            "modules": [{"name": "Adblock", "url": "missing"}],
        }
        def fetcher(url):
            if url == "good":
                return b"$done({});"
            raise HTTPError(url, 404, "Not Found", {}, None)
        self.assertEqual(self.run_main(cfg, fetcher), 1)
        self.assert_previous_files()

    def test_bad_remote_script_retains_files_and_retired_script(self):
        cfg = {
            "scripts": [{"name": "ad.js", "url": "good"}],
            "modules": [{"name": "Adblock", "url": "module"}],
            "retired_scripts": ["ad.js"],
        }
        responses = {
            "good": b"$done({});",
            "module": b"[Script]\na=type=http-response,script-path=https://example.com/ad.js\n",
            "https://example.com/ad.js": b"<!DOCTYPE html><html>homepage</html>",
        }
        self.assertEqual(self.run_main(cfg, responses.__getitem__), 1)
        self.assert_previous_files()

    def test_html_module_cannot_replace_valid_module(self):
        cfg = {"modules": [{"name": "Adblock", "url": "module"}]}
        self.assertEqual(self.run_main(cfg, lambda _: b"<html>homepage</html>"), 1)
        self.assert_previous_files()

    def test_self_hosted_reference_uses_staged_script_and_publishes_pairs(self):
        cfg = {
            "scripts": [{"name": "new.js", "url": "script"}],
            "modules": [{"name": "Adblock", "url": "module"}],
        }
        module = b"#!name=new\n[Script]\na=type=http-response,script-path=https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/scripts/new.js\n"
        responses = {"script": b"$done({});", "module": module}
        self.assertEqual(self.run_main(cfg, responses.__getitem__), 0)
        self.assertEqual((self.scripts / "new.js").read_bytes(), b"$done({});")
        actual = (self.modules / "Adblock.module").read_bytes()
        self.assertIn(b"script-path=" + sync.RAW_BASE.encode() + b"new.js", actual)
        self.assertIn(b"#!raw-url=https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Adblock.module", actual)
        self.assertEqual((self.modules / "Adblock.sgmodule").read_bytes(), actual)

    def test_retirement_removes_old_rules_and_script(self):
        cfg = {
            "retired_modules": [{"name": "Adblock", "reason": "upstream missing", "replacement": "new"}],
            "retired_scripts": ["ad.js"],
        }
        self.assertEqual(self.run_main(cfg, lambda _: self.fail("Unexpected network request")), 0)
        module = (self.modules / "Adblock.sgmodule").read_text()
        self.assertNotIn("DOMAIN,example.com", module)
        self.assertIn("已停用", module)
        self.assertFalse((self.scripts / "ad.js").exists())

    def test_mirrored_source_is_refreshed_even_when_existing_module_uses_own_url(self):
        cfg = {"modules": [{"name": "Adblock", "url": "module"}]}
        module = b"[Script]\nad=type=http-response,script-path=https://example.com/ad.js\n"
        responses = {"module": module, "https://example.com/ad.js": b"$done({body:'first'});"}
        self.assertEqual(self.run_main(cfg, responses.__getitem__), 0)
        manifest = json.loads((self.scripts / "upstream.json").read_text())
        relative = next(iter(manifest["scripts"]))
        self.assertEqual(manifest["scripts"][relative]["url"], "https://example.com/ad.js")
        responses["https://example.com/ad.js"] = b"$done({body:'second'});"
        # Adblock 未在配置中重新下载时，也必须依据来源记录更新脚本。
        self.assertEqual(self.run_main({}, responses.__getitem__), 0)
        self.assertEqual((self.scripts / relative).read_bytes(), responses["https://example.com/ad.js"])

    def test_commented_script_is_not_downloaded_or_rewritten(self):
        module = b"[Script]\n# disabled=script-path=https://example.com/disabled.js\n[Rule]\nDOMAIN,example.com,REJECT\n"
        self.assertEqual(self.run_main({"modules": [{"name": "Adblock", "url": "module"}]}, lambda _: module), 0)
        self.assertIn(b"# disabled=script-path=https://example.com/disabled.js", (self.modules / "Adblock.module").read_bytes())

    def test_missing_bundle_member_prevents_all_publication(self):
        cfg = {"bundles": [{"name": "DailyAds", "members": ["missing"], "desc": "ads"}]}
        self.assertEqual(self.run_main(cfg, lambda _: self.fail("Unexpected fetch")), 1)
        self.assert_previous_files()

    def test_unused_mirror_is_removed_only_after_successful_validation(self):
        folder = self.scripts / "mirrors"
        folder.mkdir()
        old = folder / "old.js"
        old.write_bytes(b"$done({});")
        self.assertEqual(self.run_main({"modules": [{"name": "Adblock", "url": "bad"}]}, lambda _: b"<html>"), 1)
        self.assertTrue(old.exists())
        self.assertEqual(self.run_main({}, lambda _: self.fail("Unexpected fetch")), 0)
        self.assertFalse(old.exists())


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.modules = {
            sync.OUTPUT_DIR / "a.sgmodule": b"#!author=Alice\n[Rule]\nDOMAIN,ads.example,REJECT\n[Script]\nshared=type=http-response,script-path=https://example.com/a.js\n[MITM]\nhostname = %APPEND% a.example, shared.example\n",
            sync.OUTPUT_DIR / "b.sgmodule": b"#!author=Bob\n[Rule]\nDOMAIN,ads.example,REJECT\n[Map Local]\n^https://b.example/ad data-type=text data=\"{}\" header=\"Content-Type:application/json\"\n[Script]\nshared=type=http-request,script-path=https://example.com/b.js\n[MITM]\nhostname = b.example, shared.example\n",
        }

    def test_bundle_preserves_rules_names_and_mitm_without_overwriting(self):
        result = sync.merge_modules("DailyAds", ["a", "b"], self.modules, "test").decode()
        self.assertEqual(result.count("DOMAIN,ads.example,REJECT"), 1)
        self.assertIn("a.001 = type=http-response", result)
        self.assertIn("b.001 = type=http-request", result)
        self.assertEqual(result.count("hostname ="), 1)
        self.assertIn("hostname = %APPEND% a.example, shared.example, b.example", result)
        self.assertIn('data="{}" header="Content-Type:application/json"', result)
        self.assertIn("# a: Alice", result)
        self.assertIn("# b: Bob", result)

    def test_conflicting_mitm_settings_fail_instead_of_silently_overwriting(self):
        self.modules[sync.OUTPUT_DIR / "a.sgmodule"] += b"h2 = true\n"
        self.modules[sync.OUTPUT_DIR / "b.sgmodule"] += b"h2 = false\n"
        with self.assertRaisesRegex(ValueError, "冲突"):
            sync.merge_modules("DailyAds", ["a", "b"], self.modules, "test")

    def test_unsupported_section_cannot_be_silently_dropped(self):
        self.modules[sync.OUTPUT_DIR / "b.sgmodule"] += b"[General]\nunknown-setting=true\n"
        with self.assertRaisesRegex(ValueError, "暂不支持"):
            sync.merge_modules("DailyAds", ["a", "b"], self.modules, "test")

    def test_repository_links_cannot_escape_scripts_directory(self):
        with self.assertRaises(ValueError):
            sync.local_script_path(sync.RAW_BASE + "%2e%2e/config/upstream.yml")


class SelectedSourceTests(unittest.TestCase):
    def test_real_cainiao_grouped_patterns_preserve_services_and_keep_ads(self):
        cfg = yaml.safe_load(sync.CONFIG_PATH.read_text())
        patterns = sync.compile_filters(cfg["filters"])["cainiao_preserve_services"]
        content = r"""[Script]
service = type=http-response,pattern=nbpresentation\.(pickup\.empty\.page|protocol\.homepage)\.get,script-path=https://example.com/services.js
ad = type=http-response,pattern=nbnetflow\.ads\.m?show,script-path=https://example.com/ads.js
[Map Local]
nbpresentation\.(homepage\.merge|tabbar\.marketing)\.get data-type=text data="{}"
"""
        filtered, _ = sync.apply_filter(content, patterns)
        self.assertNotIn("services.js", filtered)
        self.assertNotIn("tabbar", filtered)
        self.assertIn("ads.js", filtered)


if __name__ == "__main__":
    unittest.main()
