---
name: laotie-auto-cut
description: LAOTIE 自动快剪（老铁剪映快剪）：剪映专业版（JianYing Pro）素材自动剪辑技能。把素材文件夹或单个素材一键变成剪映草稿：自动收集视频/图片/音频、探测画幅、导入主轨、配背景音乐、加动画标题，并用草稿检查器自动验证结构。当用户要求“用剪映剪视频/剪一段/做草稿/素材快速成片/Vlog/把 XX 文件夹剪成视频/自动剪辑”且涉及本地媒体文件时使用。依赖已安装的 jianying-editor 技能（提供 JyProject API）。
---

# LAOTIE 自动快剪（剪映自动剪辑）

固定自动任务：**环境检查 → 自动剪辑 → 草稿验证** 三步出剪映草稿。
依赖：`jianying-editor` 技能（同一 `.user_skills` 目录下的兄弟技能）+ ffmpeg/ffprobe + 剪映专业版草稿目录。

## 一键流程

```bash
# 1) 环境检查（缺项先修复再继续）
python <SKILL_ROOT>/scripts/env_check.py

# 2) 自动剪辑：素材文件夹 → 剪映草稿
python <SKILL_ROOT>/scripts/auto_edit.py --assets-dir "D:\素材" --name "草稿名" [--bgm "bgm.mp3"] [--titles "标题一|标题二"] [--ratio 16:9|9:16] [--clip-duration 5] [--max-clips 10]

# 3) 验证草稿结构
python <SKILL_ROOT>/scripts/verify_draft.py --name "草稿名" [--expect-video 1] [--expect-audio 1] [--expect-text 2]
```

单素材模式：`--video <文件>` / `--image <文件>` / `--audio <文件>` 可直接指定，不必用文件夹。

## 自动任务规则

- **画幅匹配**：主视频宽>高 → 横屏 1920x1080；高>宽 → 竖屏 1080x1920（自动探测）。素材比例特殊时显式传 `--ratio`，防止黑边。
- **主轨导入**：素材按文件名排序，最多 `--max-clips`(默认10) 段；视频默认用自身时长，图片默认 3 秒，可用 `--clip-duration` 统一覆盖。
- **BGM**：默认取素材文件夹第一个音频，或用 `--bgm` 指定；时长默认铺满主轨总时长，可用 `--duration` 覆盖。
- **标题**：`--titles "A|B"` 按 `|` 分隔，自动间隔放置并轮换动画（复古打字机/向右滑动等），同轨标题不重叠。
- **保存后提醒用户**：重启剪映（或进入任一旧草稿再退出）才能看到新草稿；剪映不会实时刷新草稿列表。
- **媒体解析**：依赖 ffprobe/ffmpeg（`env_check.py` 会检查；缺失时先 `winget install Gyan.FFmpeg`）。素材非标准尺寸时自动归一化转码。

## 验收标准

草稿目录存在于剪映草稿根；视频轨 ≥1 段；指定了 BGM 则音频轨 ≥1 段；指定了标题则字幕轨文字数量匹配。全部满足才算完成。

## 进阶能力（转交 jianying-editor 技能）

配音+字幕一键出片（`add_narrated_subtitles` TTS）、录屏+智能变焦、网页动效转视频、特效/转场/滤镜、自动导出 MP4（`scripts/auto_exporter.py`）。
常用 API 摘要见 [references/jianying-editor-api.md](references/jianying-editor-api.md)，完整规则直接读 `jianying-editor/SKILL.md` 与其 `rules/`。
