#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""环境检查：jianying-editor 技能、ffmpeg/ffprobe、剪映草稿目录。

退出码 0 = 全部就绪；1 = 存在缺失项。
输出 JSON：{"pass": bool, "checks": {...}, "draft_root": "..."}
"""
import json
import os
import sys

from common import ensure_ffmpeg_on_path, find_jy_skill_root


def probe_draft_root() -> str:
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "JianyingPro", "User Data", "Projects", "com.lveditor.draft"),
        os.path.expanduser(r"~\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return ""


def main() -> int:
    checks = {}

    try:
        root = find_jy_skill_root()
        checks["jianying_editor"] = bool(root)
    except FileNotFoundError as e:
        checks["jianying_editor"] = False
        print(f"⚠️ {e}")

    ensure_ffmpeg_on_path()
    checks["ffmpeg"] = bool(os.environ.get("PATH") and _which("ffmpeg"))
    checks["ffprobe"] = bool(os.environ.get("PATH") and _which("ffprobe"))

    draft = probe_draft_root()
    checks["draft_root"] = bool(draft)

    ok = all(checks.values())
    print(json.dumps({"pass": ok, "checks": checks, "draft_root": draft}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def _which(name: str) -> bool:
    import shutil
    return shutil.which(name) is not None


if __name__ == "__main__":
    sys.exit(main())
