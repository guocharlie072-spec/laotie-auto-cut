# -*- coding: utf-8 -*-
"""jianying-auto-edit 技能公共工具：定位 jianying-editor 技能与 FFmpeg。"""
import os
import shutil


def find_jy_skill_root() -> str:
    """定位已安装的 jianying-editor 技能根目录（包含 scripts/jy_wrapper.py）。"""
    # 本文件位于 <user_skills>/jianying-auto-edit/scripts/common.py
    user_skills_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.environ.get("JY_SKILL_ROOT", "").strip(),
        os.path.join(user_skills_root, "jianying-editor"),
        os.path.join(user_skills_root, "jianying-editor-skill"),
    ]
    for cand in candidates:
        if cand and os.path.exists(os.path.join(cand, "scripts", "jy_wrapper.py")):
            return cand
    raise FileNotFoundError(
        "找不到 jianying-editor 技能（需要其 scripts/jy_wrapper.py）。"
        "请确认已安装 luoluoluo22/jianying-editor-skill。"
    )


def ensure_ffmpeg_on_path() -> None:
    """若 PATH 中缺少 ffprobe，尝试把 winget 安装的 FFmpeg bin 目录加入 PATH。"""
    if shutil.which("ffprobe"):
        return
    links = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Links")
    if os.path.exists(os.path.join(links, "ffprobe.exe")):
        os.environ["PATH"] = links + os.pathsep + os.environ.get("PATH", "")
        return
    pkgs = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if os.path.isdir(pkgs):
        for d in os.listdir(pkgs):
            if "Gyan.FFmpeg" in d:
                base = os.path.join(pkgs, d)
                for sub in os.listdir(base):
                    bin_dir = os.path.join(base, sub, "bin")
                    if os.path.exists(os.path.join(bin_dir, "ffprobe.exe")):
                        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                        return
    for extra in [
        r"C:\ffmpeg\bin",
        os.path.join(os.environ.get("PROGRAMFILES", ""), "ffmpeg", "bin"),
    ]:
        if os.path.exists(os.path.join(extra, "ffprobe.exe")):
            os.environ["PATH"] = extra + os.pathsep + os.environ.get("PATH", "")
            return
