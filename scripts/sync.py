#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从上游自动同步模块到 modules/ 目录

用法:
    python scripts/sync.py

支持按模块配置过滤规则(见 config/upstream.yml 中 filters), 用于剔除
某些上游模块里与特定 App 相关的规则, 避免多模块重复 MITM 造成的接口异常。
"""

import hashlib
import os
import re
import sys
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "upstream.yml")
OUTPUT_DIR = os.path.join(ROOT, "modules")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (sync-bot)"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def compile_filters(filters_cfg):
    """把 filters 配置编译成正则列表(忽略转义反斜杠, 兼容 `\\.` 形式的规则)"""
    compiled = {}
    for name, cfg in (filters_cfg or {}).items():
        patterns = cfg.get("patterns", []) if isinstance(cfg, dict) else []
        compiled[name] = [re.compile(p.replace("\\", ""), re.IGNORECASE) for p in patterns]
    return compiled


def line_match(line: str, patterns) -> bool:
    """对去除反斜杠后的行进行匹配, 兼容转义/非转义两种 URL 写法"""
    return any(p.search(line.replace("\\", "")) for p in patterns)


def apply_filter(content: str, patterns) -> str:
    """从模块内容中剔除命中的规则行, 并清理 MITM 域名列表"""
    lines = content.split("\n")
    out = []
    section = None
    removed = 0
    for line in lines:
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1].strip()
            out.append(line)
            continue
        # 模块元信息(#!name/#!desc等)永远保留
        if s.startswith("#!"):
            out.append(line)
            continue
        # MITM 域名列表按 token 过滤, 而不是整行删除
        if section == "MITM" and s.startswith("hostname"):
            tokens = [t for t in line.split(",") if t.strip()]
            kept = [t for t in tokens if not line_match(t, patterns)]
            if len(kept) != len(tokens):
                removed += len(tokens) - len(kept)
            new_line = ", ".join(t.strip() for t in kept)
            if new_line.strip():
                out.append(new_line)
            continue
        # 其余规则行整体删除
        if line_match(line, patterns):
            removed += 1
            continue
        out.append(line)
    return "\n".join(out), removed


def main() -> int:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    filters = compile_filters(cfg.get("filters", {}))
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for mod in cfg.get("modules", []):
        name = mod["name"]
        url = mod["url"]
        out_path = os.path.join(OUTPUT_DIR, f"{name}.sgmodule")

        try:
            data = fetch(url)
            content = data.decode("utf-8", errors="replace")
        except Exception as e:
            print(f"[FAILED]   {name}.sgmodule: {e}")
            continue

        filter_name = mod.get("filter")
        if filter_name and filter_name in filters:
            content, removed = apply_filter(content, filters[filter_name])
            if removed:
                print(f"[FILTER]   {name}.sgmodule 剔除 {removed} 条规则 (filter: {filter_name})")
            content = content.encode("utf-8")
            data = content

        new_hash = hashlib.sha256(data).digest()
        old_hash = None
        if os.path.exists(out_path):
            with open(out_path, "rb") as f:
                old_hash = hashlib.sha256(f.read()).digest()

        if old_hash == new_hash:
            print(f"[no change] {name}.sgmodule")
            continue

        with open(out_path, "wb") as f:
            f.write(data)
        print(f"[updated]   {name}.sgmodule ({len(data)} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())