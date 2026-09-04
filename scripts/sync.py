#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从上游自动同步模块到 modules/ 目录

用法:
    python scripts/sync.py

支持按模块配置过滤规则(见 config/upstream.yml 中 filters), 用于剔除
某些上游模块里与特定 App 相关的规则, 避免多模块重复 MITM 造成的接口异常。

BiliUniverse 模块的 bundle 脚本托管在 github.com Release 下载(国内访问
不稳定, 会导致 Shadowrocket 拉脚本超时、请求被丢弃)。sync.py 会把它们
下载到 scripts/ 目录并重写 script-path 为 raw.githubusercontent.com 直链。
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
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
RAW_BASE = "https://raw.githubusercontent.com/Maxworkinghard/module/main/scripts/"

# 需要重写的上游脚本地址: github.com Release 资产 -> 同步到本仓库 raw 直链
SCRIPT_URL_RE = re.compile(r"https://github\.com/[^/]+/[^/]+/releases/download/[^/\s]+/([^\s,]+)")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (sync-bot)"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def rewrite_scripts(name: str, content: str) -> str:
    """把模块内 github.com Release 的 script-path 重写为本仓库 raw 直链,
    并将对应 bundle 脚本下载保存到 scripts/ 目录(由 workflow 一起提交)。
    """
    def repl(m: re.Match) -> str:
        src = m.group(0)
        fname = m.group(1)
        local = os.path.join(SCRIPTS_DIR, f"{name}.{fname}")
        try:
            data = fetch(src)
        except Exception as e:
            print(f"[WARN]    {name}.sgmodule 脚本下载失败 {src}: {e}")
            return src
        changed = True
        if os.path.exists(local):
            with open(local, "rb") as f:
                changed = hashlib.sha256(f.read()).digest() != hashlib.sha256(data).digest()
        with open(local, "wb") as f:
            f.write(data)
        if changed:
            print(f"[script]  {name}.sgmodule 更新脚本 -> scripts/{name}.{fname}")
        return RAW_BASE + f"{name}.{fname}"

    return SCRIPT_URL_RE.sub(repl, content)


def strip_http_request(content: str) -> str:
    """剔除 type=http-request 规则行(BiliUniverse 官方不支持 Shadowrocket,
    其前置拦截脚本在 Shadowrocket 上执行失败会导致请求被丢弃)"""
    out = []
    removed = 0
    in_script = False
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            in_script = s == "[Script]"
            out.append(line)
            continue
        if in_script and re.search(r"type=http-request\b", s):
            removed += 1
            continue
        out.append(line)
    return "\n".join(out), removed


def strip_scripts(content: str) -> str:
    """删除整个 [Script] 段(BiliUniverse 官方不支持 Shadowrocket,
    其 http-response/http-request 脚本执行失败会吞掉响应, 导致 App 显示无网络)"""
    lines = content.split("\n")
    out = []
    in_script = False
    removed = 0
    for line in lines:
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            if in_script:
                removed += 1  # 段尾(下一个段标题)
            in_script = s == "[Script]"
            if not in_script:
                out.append(line)
            continue
        if in_script:
            if s and not s.startswith("#"):
                removed += 1
            continue
        out.append(line)
    return "\n".join(out).rstrip() + "\n", removed


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


def sync_scripts(scripts_cfg: list):
    """从上游独立同步 JS 脚本到 scripts/ 目录"""
    if not scripts_cfg:
        return
    print("=== 开始同步独立上游脚本 ===")
    for item in scripts_cfg:
        name = item["name"]
        url = item["url"]
        local_path = os.path.join(SCRIPTS_DIR, name)
        try:
            data = fetch(url)
        except Exception as e:
            print(f"[FAILED]   script {name}: {e}")
            continue

        changed = True
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                changed = hashlib.sha256(f.read()).digest() != hashlib.sha256(data).digest()

        if changed:
            with open(local_path, "wb") as f:
                f.write(data)
            print(f"[updated]  script -> scripts/{name} ({len(data)} bytes)")
        else:
            print(f"[no change] script scripts/{name}")


def sync_module_pairs():
    """保证 modules/ 目录下所有 .sgmodule 与 .module 保持成对存在且内容一致"""
    print("=== 检查并同步 .sgmodule 与 .module 双格式 ===")
    all_files = os.listdir(OUTPUT_DIR)
    for fname in sorted(all_files):
        if fname.endswith(".sgmodule"):
            base = fname[:-9]
            mod_name = f"{base}.module"
            src = os.path.join(OUTPUT_DIR, fname)
            dst = os.path.join(OUTPUT_DIR, mod_name)
            if not os.path.exists(dst) or open(src, "rb").read() != open(dst, "rb").read():
                with open(src, "rb") as f_src, open(dst, "wb") as f_dst:
                    f_dst.write(f_src.read())
                print(f"[sync-pair] {fname} -> {mod_name}")
        elif fname.endswith(".module"):
            base = fname[:-7]
            sg_name = f"{base}.sgmodule"
            src = os.path.join(OUTPUT_DIR, fname)
            dst = os.path.join(OUTPUT_DIR, sg_name)
            if not os.path.exists(dst) or open(src, "rb").read() != open(dst, "rb").read():
                with open(src, "rb") as f_src, open(dst, "wb") as f_dst:
                    f_dst.write(f_src.read())
                print(f"[sync-pair] {fname} -> {sg_name}")


def main() -> int:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    filters = compile_filters(cfg.get("filters", {}))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DIR, exist_ok=True)

    # 1. 同步独立脚本
    sync_scripts(cfg.get("scripts", []))

    # 2. 同步上游模块
    print("=== 开始同步上游模块 ===")
    for mod in cfg.get("modules", []):
        name = mod["name"]
        url = mod["url"]
        out_path_sg = os.path.join(OUTPUT_DIR, f"{name}.sgmodule")
        out_path_mod = os.path.join(OUTPUT_DIR, f"{name}.module")

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

        # 重写 github.com Release 脚本直链为仓库 raw 直链并同步脚本
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        if mod.get("strip_http_request"):
            content, removed = strip_http_request(content)
            if removed:
                print(f"[STRIP]    {name}.sgmodule 剔除 {removed} 条 http-request 规则")
        if mod.get("strip_scripts"):
            content, removed = strip_scripts(content)
            if removed:
                print(f"[STRIP]    {name}.sgmodule 删除整个 [Script] 段 ({removed} 行)")
        content = rewrite_scripts(name, content)
        data = content.encode("utf-8")

        new_hash = hashlib.sha256(data).digest()
        old_hash = None
        if os.path.exists(out_path_sg):
            with open(out_path_sg, "rb") as f:
                old_hash = hashlib.sha256(f.read()).digest()

        if old_hash == new_hash and os.path.exists(out_path_mod):
            print(f"[no change] {name}.sgmodule & {name}.module")
            continue

        with open(out_path_sg, "wb") as f:
            f.write(data)
        with open(out_path_mod, "wb") as f:
            f.write(data)
        print(f"[updated]   {name}.sgmodule & {name}.module ({len(data)} bytes)")

    # 3. 检查并补齐所有模块的双格式
    sync_module_pairs()

    return 0



if __name__ == "__main__":
    sys.exit(main())