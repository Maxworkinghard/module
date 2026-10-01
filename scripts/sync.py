#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步模块及脚本；全部来源和脚本引用通过检查后才写入文件。"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "upstream.yml"
OUTPUT_DIR = ROOT / "modules"
SCRIPTS_DIR = ROOT / "scripts"
RAW_BASE = "https://raw.githubusercontent.com/Maxworkinghard/module/main/scripts/"
MODULE_BASE = "https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/"
SCRIPT_PATH_RE = re.compile(r"\bscript-path\s*=\s*[\"']?(https?://[^\s,\"']+)", re.I)
HTML_RE = re.compile(
    r"^\s*(?:<!--.*?-->\s*)*(?:<!doctype\s+html\b|<(?:html|head|body)\b)",
    re.I | re.S,
)
SECTION_RE = re.compile(r"^\[([^\]]+)\]$")
MODULE_SECTIONS = {"rule", "url rewrite", "header rewrite", "body rewrite", "map local", "script", "mitm", "general"}


def validate_payload(data: bytes, kind: str, source: str, allow_arguments=False) -> str:
    """拒绝空文件、HTML 页面及无法解析为文本的下载结果。"""
    if not data.strip():
        raise ValueError(f"{source}: 下载内容为空")
    content = data.decode("utf-8-sig")
    if HTML_RE.search(content[:8192]):
        raise ValueError(f"{source}: 返回 HTML 网页，不能用作{kind}")
    if kind == "module":
        sections = {
            match.group(1).lower()
            for line in content.splitlines()
            if (match := SECTION_RE.match(line.strip()))
        }
        if not sections.intersection(MODULE_SECTIONS):
            raise ValueError(f"{source}: 缺少模块配置段")
        if "{{{" in content and not allow_arguments:
            raise ValueError(f"{source}: 含有未展开的模块参数")
    if kind == "script":
        result = subprocess.run(
            ["node", "--check"], input=data, capture_output=True, timeout=15
        )
        if result.returncode:
            detail = result.stderr.decode("utf-8", errors="replace").splitlines()[-7:]
            raise ValueError(f"{source}: JavaScript 语法检查失败\n" + "\n".join(detail))
    return content


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (module-sync)"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.headers.get_content_type() == "text/html":
            raise ValueError(f"{url}: 返回 HTML 网页")
        return response.read()


def compile_filters(filters_cfg):
    # 保留过滤表达式自身的转义；只在匹配时处理上游 URL 正则中的反斜杠。
    return {
        name: [re.compile(pattern, re.I) for pattern in cfg.get("patterns", [])]
        for name, cfg in (filters_cfg or {}).items()
    }


def line_match(line: str, patterns) -> bool:
    return any(pattern.search(line.replace("\\", "")) for pattern in patterns)


def apply_filter(content: str, patterns):
    """剔除专用 App 的规则；MITM 域名按项过滤并保留 hostname 赋值及 APPEND。"""
    output = []
    section = ""
    removed = 0
    for line in content.splitlines():
        stripped = line.strip()
        if match := SECTION_RE.match(stripped):
            section = match.group(1).lower()
            output.append(line)
            continue
        if stripped.startswith("#!"):
            output.append(line)
            continue
        if section == "mitm" and re.match(r"hostname\s*=", stripped, re.I):
            value = line.split("=", 1)[1].strip()
            append = re.match(r"%APPEND%\s*", value, re.I)
            if append:
                value = value[append.end():]
            hosts = [host.strip() for host in value.split(",") if host.strip()]
            kept = [host for host in hosts if not line_match(host, patterns)]
            removed += len(hosts) - len(kept)
            if kept:
                prefix = "%APPEND% " if append else ""
                output.append("hostname = " + prefix + ", ".join(kept))
            continue
        if not stripped.startswith("#") and line_match(line, patterns):
            removed += 1
            continue
        output.append(line)
    return "\n".join(output).rstrip() + "\n", removed


def collect_script_urls(content: str):
    urls = set()
    in_script = False
    for line in content.splitlines():
        stripped = line.strip()
        if match := SECTION_RE.match(stripped):
            in_script = match.group(1).lower() == "script"
            continue
        if not in_script or not stripped or stripped.startswith("#"):
            continue
        match = SCRIPT_PATH_RE.search(stripped)
        if not match:
            raise ValueError(f"脚本规则缺少有效的 script-path: {stripped[:100]}")
        urls.add(match.group(1))
    return urls


def local_script_path(url: str):
    """本仓库 Raw/CDN 链接检查待发布文件，避免误读 CDN 上的旧缓存。"""
    parsed = urlsplit(url)
    prefixes = {
        "raw.githubusercontent.com": "/Maxworkinghard/module/main/scripts/",
        "fastly.jsdelivr.net": "/gh/Maxworkinghard/module@main/scripts/",
        "cdn.jsdelivr.net": "/gh/Maxworkinghard/module@main/scripts/",
    }
    prefix = prefixes.get(parsed.hostname)
    if prefix and parsed.path.startswith(prefix):
        filename = unquote(parsed.path[len(prefix):])
        relative = Path(filename)
        if not filename or relative.is_absolute() or ".." in relative.parts or "\\" in filename:
            raise ValueError(f"无效的本仓库脚本路径: {url}")
        return SCRIPTS_DIR / filename
    return None


def mirror_scripts(modules: dict, staged: dict, declared: list):
    """统一镜像所有 script-path，保留来源与哈希；下一次仍从作者 URL 更新。"""
    manifest_path = SCRIPTS_DIR / "upstream.json"
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    previous_by_path = {
        SCRIPTS_DIR / relative: item["url"]
        for relative, item in previous.get("scripts", {}).items()
    }
    declared_by_url = {item["url"]: SCRIPTS_DIR / item["name"] for item in declared}
    references = {}
    for path, data in modules.items():
        for url in collect_script_urls(data.decode("utf-8-sig")):
            references.setdefault(url, set()).add(path.stem)

    sources = {}
    destinations = {}
    for url in sorted(references):
        local = local_script_path(url)
        source = previous_by_path.get(local, url) if local else url
        # 人工维护的本仓库脚本只规范化 Raw 地址；声明过的上游已在本轮下载。
        if local and local not in previous_by_path:
            destinations[url] = local
            continue
        if source in declared_by_url:
            destinations[url] = declared_by_url[source]
            continue
        filename = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(urlsplit(source).path).name)[:80]
        filename = filename or "script.js"
        identity = hashlib.sha256(source.encode()).hexdigest()[:16]
        destination = SCRIPTS_DIR / "mirrors" / f"{identity}-{filename}"
        destinations[url] = destination
        sources.setdefault(source, {"path": destination, "modules": set()})["modules"].update(references[url])

    def download(source):
        data = fetch(source)
        validate_payload(data, "script", source)
        return data

    errors = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(download, source): source for source in sources}
        for future in as_completed(futures):
            source = futures[future]
            try:
                staged[sources[source]["path"]] = future.result()
            except Exception as error:
                errors.append(f"{source}: {error}")
    if errors:
        raise ValueError("脚本镜像检查失败:\n" + "\n".join(sorted(errors)))

    manifest = {"format": 1, "scripts": {}}
    for source, item in sorted(sources.items()):
        relative = item["path"].relative_to(SCRIPTS_DIR).as_posix()
        manifest["scripts"][relative] = {
            "url": source,
            "sha256": hashlib.sha256(staged[item["path"]]).hexdigest(),
            "modules": sorted(item["modules"]),
        }
    staged[manifest_path] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()

    for path, data in list(modules.items()):
        output = []
        in_script = False
        for line in data.decode("utf-8-sig").splitlines():
            if match := SECTION_RE.match(line.strip()):
                in_script = match.group(1).lower() == "script"
            if in_script and line.strip() and not line.lstrip().startswith("#"):
                def replace(match):
                    destination = destinations[match.group(1)]
                    url = RAW_BASE + destination.relative_to(SCRIPTS_DIR).as_posix()
                    return match.group(0).replace(match.group(1), url)
                line = SCRIPT_PATH_RE.sub(replace, line)
            output.append(line)
        modules[path] = ("\n".join(output).rstrip() + "\n").encode()
    unused = {path for path in (SCRIPTS_DIR / "mirrors").glob("*") if path.is_file()} - {
        item["path"] for item in sources.values()
    }
    print(f"[mirrored] {len(sources)} 个上游脚本；模块仅使用本仓库脚本地址")
    return unused


def merge_modules(name: str, members: list, modules: dict, description: str) -> bytes:
    """按段合并模块，保留署名、去重规则，避免重复脚本名称覆盖及 MITM 赋值覆盖。"""
    order = ["Rule", "URL Rewrite", "Header Rewrite", "Body Rewrite", "Map Local", "Script", "MITM"]
    sections = {section.lower(): [] for section in order}
    seen = {section.lower(): set() for section in order}
    hosts = []
    mitm_options = {}
    credits = []
    for member in members:
        path = OUTPUT_DIR / f"{member}.sgmodule"
        if path not in modules:
            raise ValueError(f"合集 {name} 缺少模块 {member}")
        content = modules[path].decode("utf-8-sig")
        author = re.search(r"^#!author=(.*)$", content, re.M)
        homepage = re.search(r"^#!homepage=(.*)$", content, re.M)
        credits.append(f"# {member}: " + (author.group(1) if author else "Maxworkinghard/module"))
        if homepage:
            credits.append("# " + homepage.group(1))
        section = None
        script_number = 0
        for line in content.splitlines():
            stripped = line.strip()
            if match := SECTION_RE.match(stripped):
                section = match.group(1).lower()
                if section not in sections:
                    raise ValueError(f"合集 {name} 暂不支持 [{match.group(1)}]，来源 {member}")
                continue
            if not section or not stripped or stripped.startswith("#"):
                continue
            if section == "mitm":
                key, value = (part.strip() for part in stripped.split("=", 1))
                if key.lower() == "hostname":
                    value = re.sub(r"^%APPEND%\s*", "", value, flags=re.I)
                    for host in value.split(","):
                        host = host.strip()
                        if host and host not in hosts:
                            hosts.append(host)
                else:
                    if key in mitm_options and mitm_options[key] != value:
                        raise ValueError(f"合集 {name} 的 MITM {key} 设置冲突")
                    mitm_options[key] = value
                continue
            signature = stripped
            if section == "script":
                if "=" not in stripped:
                    raise ValueError(f"{member}: 无效脚本规则")
                _, settings = stripped.split("=", 1)
                signature = re.sub(r"\s*,\s*", ",", settings.strip())
                script_number += 1
                stripped = f"{member}.{script_number:03d} = {settings.strip()}"
            if signature not in seen[section]:
                seen[section].add(signature)
                sections[section].append(stripped)
    sections["mitm"] = (["hostname = %APPEND% " + ", ".join(hosts)] if hosts else []) + [
        f"{key} = {value}" for key, value in mitm_options.items()
    ]
    output = [
        f"#!name={name} · 日用去广告合集", f"#!desc={description}",
        "#!homepage=https://github.com/Maxworkinghard/module",
        f"#!raw-url={MODULE_BASE}{name}.module", "#!category=广告拦截",
        "# AWAvenue 广告规则遵循 GPL-3.0；见 licenses/AWAvenue-GPL-3.0.txt。",
        "# 合集内规则来自以下模块，原作者署名及完整来源见各模块与 scripts/upstream.json。",
        *credits,
    ]
    for section in order:
        if sections[section.lower()]:
            output.extend(["", f"[{section}]", *sections[section.lower()]])
    return ("\n".join(output) + "\n").encode()


def validate_script_references(modules: dict, staged: dict, retired_scripts: set):
    references = {}
    for path, data in modules.items():
        content = validate_payload(data, "module", str(path))
        for url in collect_script_urls(content):
            references.setdefault(url, []).append(path.name)

    errors = []
    remote_urls = []
    for url in sorted(references):
        try:
            local = local_script_path(url)
            if local is None:
                remote_urls.append(url)
                continue
            if local in retired_scripts:
                raise ValueError(f"仍引用待移除脚本 {local.name}")
            data = staged[local] if local in staged else local.read_bytes()
            validate_payload(data, "script", url)
        except Exception as error:
            errors.append(f"{', '.join(references[url])}: {url}: {error}")

    def check_remote(url):
        validate_payload(fetch(url), "script", url)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(check_remote, url): url for url in remote_urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as error:
                errors.append(f"{', '.join(references[url])}: {url}: {error}")
    if errors:
        raise ValueError("脚本引用检查失败:\n" + "\n".join(sorted(errors)))
    print(f"[checked] {len(references)} 个不同脚本链接，其中 {len(remote_urls)} 个远程来源")


def retired_module(item: dict) -> bytes:
    """旧订阅地址提供停用提示；刷新后移除旧规则，无需依赖 404 清理客户端。"""
    replacement = item.get("replacement")
    description = item["reason"]
    if replacement:
        description += f"；请停用此模块并启用 {replacement}"
    return (
        f"#!name=已停用：{item['name']}\n"
        f"#!desc={description}\n"
        "#!homepage=https://github.com/Maxworkinghard/module\n"
        "\n[Rule]\n# 兼容旧订阅地址；不再加载脚本或拦截请求。\n"
    ).encode("utf-8")


def set_metadata(content: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^#!{re.escape(key)}=.*$", re.M)
    line = f"#!{key}={value}"
    return pattern.sub(lambda _: line, content) if pattern.search(content) else line + "\n" + content


def configure_script_arguments(content: str, arguments: dict) -> str:
    """当前 Sparkle 脚本使用 JSON 参数；覆盖上游尚未更新的参数模板。"""
    output = []
    matched = set()
    in_script = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(("#!arguments=", "#!arguments-desc=")):
            continue
        if match := SECTION_RE.match(stripped):
            in_script = match.group(1).lower() == "script"
        if in_script and stripped and not stripped.startswith("#") and "=" in stripped:
            name = stripped.split("=", 1)[0].strip()
            if name in arguments:
                line = re.sub(r",\s*argument=.*$", "", line)
                value = json.dumps(arguments[name], ensure_ascii=False, separators=(",", ":"))
                line += f', argument="{value}"'
                matched.add(name)
        output.append(line)
    if missing := set(arguments) - matched:
        raise ValueError(f"上游缺少配置参数的脚本: {', '.join(sorted(missing))}")
    return "\n".join(output).rstrip() + "\n"


def unique_script_names(content: str, prefix: str) -> str:
    """同一模块中重复的名字可能覆盖前一条脚本；保留首条并给其余条目独立名字。"""
    output = []
    names = set()
    in_script = False
    number = 0
    for line in content.splitlines():
        stripped = line.strip()
        if match := SECTION_RE.match(stripped):
            in_script = match.group(1).lower() == "script"
        elif in_script and stripped and not stripped.startswith("#"):
            name, settings = stripped.split("=", 1)
            name = name.strip()
            if name in names:
                while True:
                    number += 1
                    name = f"{prefix}.{number:03d}"
                    if name not in names:
                        break
                line = f"{name} = {settings.strip()}"
            names.add(name)
        output.append(line)
    return "\n".join(output).rstrip() + "\n"


def normalize_shadowrocket_rewrites(content: str) -> str:
    """部分综合来源省略 reject 前的 '-'；补成原生 Shadowrocket 三字段语法。"""
    output = []
    in_rewrite = False
    for line in content.splitlines():
        if match := SECTION_RE.match(line.strip()):
            in_rewrite = match.group(1).lower() == "url rewrite"
        elif in_rewrite and not line.lstrip().startswith("#"):
            match = re.fullmatch(r"\s*(\S+)\s+(reject(?:-(?:200|dict|array|img|tinygif|video|drop))?)\s*", line, re.I)
            if match:
                line = f"{match.group(1)} - {match.group(2)}"
        output.append(line)
    return "\n".join(output).rstrip() + "\n"


def prepare(cfg: dict):
    """所有变更先留在内存中；任何来源失败都不写入已有模块。"""
    filters = compile_filters(cfg.get("filters"))
    staged = {}
    for item in cfg.get("scripts", []):
        source = item["url"]
        data = fetch(source)
        validate_payload(data, "script", source)
        staged[SCRIPTS_DIR / item["name"]] = data
        print(f"[fetched] script {item['name']}")

    for item in cfg.get("modules", []):
        source = item.get("url") or str(ROOT / item["file"])
        data = fetch(source) if item.get("url") else Path(source).read_bytes()
        content = validate_payload(
            data, "module", source, allow_arguments=bool(item.get("script_arguments"))
        )
        if filter_name := item.get("filter"):
            content, removed = apply_filter(content, filters[filter_name])
            print(f"[filter] {item['name']}: 剔除 {removed} 条专用 App 规则/域名")
        if display_name := item.get("display_name"):
            content = set_metadata(content, "name", display_name)
        if description := item.get("module_desc"):
            content = set_metadata(content, "desc", description)
        if author := item.get("module_author"):
            content = set_metadata(content, "author", author)
        if arguments := item.get("script_arguments"):
            content = configure_script_arguments(content, arguments)
        content = set_metadata(
            content, "raw-url",
            MODULE_BASE + item["name"] + ".module",
        )
        # 无剩余模板时移除无效的上游开关提示；已固定的脚本参数仍保留。
        content = re.sub(r"^#!arguments(?:-desc)?=.*\n?", "", content, flags=re.M)
        content = unique_script_names(content, item["name"])
        content = normalize_shadowrocket_rewrites(content)
        staged[OUTPUT_DIR / f"{item['name']}.sgmodule"] = content.encode("utf-8")

    for item in cfg.get("retired_modules", []):
        staged[OUTPUT_DIR / f"{item['name']}.sgmodule"] = retired_module(item)
    retired_scripts = {SCRIPTS_DIR / name for name in cfg.get("retired_scripts", [])}
    modules = {path: path.read_bytes() for path in OUTPUT_DIR.glob("*.sgmodule")}
    # 合集每轮重建，不能把上次合集中的镜像引用当作仍在使用的上游。
    for bundle in cfg.get("bundles", []):
        modules.pop(OUTPUT_DIR / f"{bundle['name']}.sgmodule", None)
    modules.update({path: data for path, data in staged.items() if path.suffix == ".sgmodule"})
    retired_scripts.update(mirror_scripts(modules, staged, cfg.get("scripts", [])))
    for bundle in cfg.get("bundles", []):
        modules[OUTPUT_DIR / f"{bundle['name']}.sgmodule"] = merge_modules(
            bundle["name"], bundle["members"], modules, bundle["desc"]
        )
    validate_script_references(modules, staged, retired_scripts)
    for path, data in modules.items():
        staged[path] = data
        staged[path.with_suffix(".module")] = data
    return staged, retired_scripts


def publish(staged: dict, retired_scripts: set):
    for path, data in sorted(staged.items()):
        if path.exists() and path.read_bytes() == data:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"[updated] {path.relative_to(ROOT)} ({len(data)} bytes)")
    for path in sorted(retired_scripts):
        if path.exists():
            path.unlink()
            print(f"[retired] {path.relative_to(ROOT)}")


def main() -> int:
    try:
        cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
        staged, retired_scripts = prepare(cfg)
    except Exception as error:
        print(f"[FAILED] {error}", file=sys.stderr)
        print("本次未写入模块或脚本；保留上次通过检查的版本。", file=sys.stderr)
        return 1
    publish(staged, retired_scripts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
