#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步模块及脚本；全部来源和脚本引用通过检查后才写入文件。"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
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
SCRIPT_URL_RE = re.compile(
    r"https://github\.com/[^/]+/[^/]+/releases/download/[^/\s]+/([^\s,]+)"
)
SCRIPT_PATH_RE = re.compile(r"\bscript-path\s*=\s*[\"']?(https?://[^\s,\"']+)", re.I)
HTML_RE = re.compile(
    r"^\s*(?:<!--.*?-->\s*)*(?:<!doctype\s+html\b|<(?:html|head|body)\b)",
    re.I | re.S,
)
SECTION_RE = re.compile(r"^\[([^\]]+)\]$")
MODULE_SECTIONS = {"rule", "url rewrite", "body rewrite", "map local", "script", "mitm", "general"}


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


def rewrite_scripts(name: str, content: str, staged: dict) -> str:
    """将 GitHub Release 脚本存入本仓库；下载失败时不生成损坏的模块。"""
    def replace(match):
        source = match.group(0)
        filename = f"{name}.{match.group(1)}"
        if Path(filename).name != filename:
            raise ValueError(f"无效的脚本文件名: {filename}")
        data = fetch(source)
        validate_payload(data, "script", source)
        staged[SCRIPTS_DIR / filename] = data
        return RAW_BASE + filename

    return SCRIPT_URL_RE.sub(replace, content)


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
        if Path(filename).name != filename:
            raise ValueError(f"无效的本仓库脚本路径: {url}")
        return SCRIPTS_DIR / filename
    return None


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
        source = item["url"]
        content = validate_payload(
            fetch(source), "module", source, allow_arguments=bool(item.get("script_arguments"))
        )
        if filter_name := item.get("filter"):
            content, removed = apply_filter(content, filters[filter_name])
            print(f"[filter] {item['name']}: 剔除 {removed} 条专用 App 规则/域名")
        if display_name := item.get("display_name"):
            content = set_metadata(content, "name", display_name)
        if description := item.get("module_desc"):
            content = set_metadata(content, "desc", description)
        if arguments := item.get("script_arguments"):
            content = configure_script_arguments(content, arguments)
        content = set_metadata(
            content, "raw-url",
            f"https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/{item['name']}.module",
        )
        content = rewrite_scripts(item["name"], content, staged)
        staged[OUTPUT_DIR / f"{item['name']}.sgmodule"] = content.encode("utf-8")

    for item in cfg.get("retired_modules", []):
        staged[OUTPUT_DIR / f"{item['name']}.sgmodule"] = retired_module(item)
    retired_scripts = {SCRIPTS_DIR / name for name in cfg.get("retired_scripts", [])}
    modules = {path: path.read_bytes() for path in OUTPUT_DIR.glob("*.sgmodule")}
    modules.update({path: data for path, data in staged.items() if path.suffix == ".sgmodule"})
    validate_script_references(modules, staged, retired_scripts)
    for path, data in modules.items():
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
