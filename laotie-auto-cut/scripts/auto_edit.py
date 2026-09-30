#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动剪辑：素材文件夹 / 单个素材 → 剪映草稿（一键生成）。

用法示例:
  python auto_edit.py --assets-dir "D:\\素材" --name "周末Vlog" --bgm "D:\\素材\\bgm.mp3" --titles "周末露营记|感谢观看" --ratio 16:9
  python auto_edit.py --video "D:\\video.mp4" --audio "D:\\voice.mp3" --name "解说片段" --titles "60秒看懂"

流程: 收集素材 → 探测画幅 → 建剪映工程 → 主轨导入 → 配 BGM → 加标题 → 保存草稿。
"""
import argparse
import json
import os
import sys

from common import ensure_ffmpeg_on_path, find_jy_skill_root

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac"}
TITLE_ANIMS = ["复古打字机", "向右滑动", "向上滑动", "随机弹跳"]  # 按需轮换


def probe_video(path: str):
    """返回 (width, height, duration_seconds)，失败返回 (0, 0, 0)。"""
    try:
        import cv2
        cap = cv2.VideoCapture(path)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        dur = (n / fps) if fps and n else 0.0
        return w, h, round(dur, 2)
    except Exception:
        return 0, 0, 0.0


def collect_assets(assets_dir: str):
    videos, images, audios = [], [], []
    if assets_dir and os.path.isdir(assets_dir):
        for f in sorted(os.listdir(assets_dir)):
            ext = os.path.splitext(f)[1].lower()
            full = os.path.join(assets_dir, f)
            if not os.path.isfile(full):
                continue
            if ext in VIDEO_EXTS:
                videos.append(full)
            elif ext in IMAGE_EXTS:
                images.append(full)
            elif ext in AUDIO_EXTS:
                audios.append(full)
    return videos, images, audios


def main() -> int:
    ap = argparse.ArgumentParser(description="剪映自动剪辑")
    ap.add_argument("--assets-dir", help="素材文件夹（自动收集视频/图片/音频）")
    ap.add_argument("--video", help="指定主视频文件")
    ap.add_argument("--image", help="指定主图片文件")
    ap.add_argument("--audio", help="指定旁白/音频文件")
    ap.add_argument("--name", required=True, help="剪映草稿名（显示在剪映列表）")
    ap.add_argument("--bgm", help="背景音乐文件（默认取素材文件夹第一个音频）")
    ap.add_argument("--titles", default="", help='标题列表，用 | 分隔，如 "标题一|标题二"')
    ap.add_argument("--ratio", choices=["16:9", "9:16"], default=None, help="画幅；默认按主视频自动")
    ap.add_argument("--clip-duration", type=float, default=None, help="每个素材片段时长(秒)，默认视频用自身时长、图片3秒")
    ap.add_argument("--max-clips", type=int, default=10, help="主轨最多导入的素材数(默认10)")
    ap.add_argument("--duration", type=float, default=None, help="BGM 时长(秒)，默认铺满主轨总时长")
    args = ap.parse_args()

    ensure_ffmpeg_on_path()
    skill_root = find_jy_skill_root()
    sys.path.insert(0, os.path.join(skill_root, "scripts"))
    from jy_wrapper import JyProject  # noqa: E402

    # 1. 收集素材
    videos, images, audios = collect_assets(args.assets_dir or "")
    if args.video:
        videos.insert(0, args.video)
    if args.image:
        images.insert(0, args.image)
    if args.audio:
        audios.insert(0, args.audio)
    if not videos and not images:
        print(f"❌ 没有找到视频/图片素材：{args.assets_dir or '(未指定)'}")
        return 1

    # 2. 确定画幅
    ratio = args.ratio
    if not ratio and videos:
        w, h, _ = probe_video(videos[0])
        ratio = "9:16" if (w and h and h > w) else "16:9"
    ratio = ratio or "16:9"
    width, height = (1920, 1080) if ratio == "16:9" else (1080, 1920)

    # 3. 建工程
    project = JyProject(args.name, overwrite=True, width=width, height=height)
    print(f"✅ 工程创建: {args.name} ({ratio} {width}x{height})")

    # 4. 主轨导入（Smart Append）
    total = 0.0
    clips = (videos + images)[: args.max_clips]
    for path in clips:
        ext = os.path.splitext(path)[1].lower()
        dur = None
        if ext in VIDEO_EXTS:
            w, h, d = probe_video(path)
            dur = (d if d > 0 else None)
        if args.clip_duration:
            dur = args.clip_duration
        if ext in IMAGE_EXTS and not dur:
            dur = 3.0
        try:
            seg = project.add_media_safe(path, start_time=None, duration=str(dur) if dur else None,
                                         track_name="VideoTrack")
            total += (dur or 5.0)
            print(f"  + 主轨: {os.path.basename(path)} ({dur or 'auto'}s)")
        except Exception as e:
            print(f"  ⚠️ 导入失败 {os.path.basename(path)}: {e}")
    if total <= 0:
        total = 5.0

    # 5. BGM
    bgm = args.bgm or (audios[0] if audios else None)
    if bgm and os.path.isfile(bgm):
        bdur = args.duration or round(total, 2)
        try:
            project.add_media_safe(bgm, start_time="0s", duration=f"{bdur}s", track_name="AudioTrack")
            print(f"  + 音频轨: {os.path.basename(bgm)} ({bdur}s)")
        except Exception as e:
            print(f"  ⚠️ BGM 导入失败: {e}")
    elif args.bgm:
        print(f"  ⚠️ BGM 文件不存在: {args.bgm}")

    # 6. 标题
    titles = [t.strip() for t in args.titles.split("|") if t.strip()]
    for i, t in enumerate(titles):
        start = round(0.5 + i * 2.5, 1)
        anim = TITLE_ANIMS[i % len(TITLE_ANIMS)]
        try:
            project.add_text_simple(t, start_time=f"{start}s", duration="2s", anim_in=anim)
            print(f"  + 标题: {t} @ {start}s ({anim})")
        except Exception as e:
            print(f"  ⚠️ 标题添加失败 {t}: {e}")

    # 7. 保存
    project.save()
    print(f"🎉 草稿已生成: {args.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
