#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证剪映草稿结构（封装 jianying-editor 的 draft_inspector）。

退出码 0 = 通过；1 = 失败。
按需传 --expect-video / --expect-audio / --expect-text 做数量断言。
"""
import argparse
import os
import re
import subprocess
import sys

from common import ensure_ffmpeg_on_path, find_jy_skill_root


def run_inspector(name: str):
    skill_root = find_jy_skill_root()
    inspector = os.path.join(skill_root, "scripts", "draft_inspector.py")
    proc = subprocess.run(
        [sys.executable, inspector, "summary", "--name", name],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc


def count_track(out: str, label: str):
    m = re.search(rf"- {re.escape(label)} \([^)]*\): (\d+)", out)
    return int(m.group(1)) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="剪映草稿名")
    ap.add_argument("--expect-video", type=int, default=1)
    ap.add_argument("--expect-audio", type=int, default=0)
    ap.add_argument("--expect-text", type=int, default=0)
    args = ap.parse_args()

    ensure_ffmpeg_on_path()
    proc = run_inspector(args.name)
    if proc.returncode != 0:
        print(f"❌ 草稿读取失败（{args.name}）: {(proc.stderr or proc.stdout)[-600:]}")
        return 1
    out = proc.stdout

    v = count_track(out, "VideoTrack")
    a = count_track(out, "AudioTrack")
    t = count_track(out, "Subtitles")

    issues = []
    if v is None or v < args.expect_video:
        issues.append(f"视频轨片段不足（期望>={args.expect_video}，实际={v}）")
    if a is None or a < args.expect_audio:
        issues.append(f"音频轨片段不足（期望>={args.expect_audio}，实际={a}）")
    if t is None or t < args.expect_text:
        issues.append(f"字幕轨文字不足（期望>={args.expect_text}，实际={t}）")

    print(out)
    if issues:
        print("❌ 验证未通过:")
        for i in issues:
            print(f"  - {i}")
        return 1
    print(f"✅ 草稿验证通过: {args.name}（视频{v} / 音频{a} / 文字{t}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
