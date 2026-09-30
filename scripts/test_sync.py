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
        self.assertIn(module, actual)
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


if __name__ == "__main__":
    unittest.main()
