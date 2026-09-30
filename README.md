# LAOTIE 自动快剪（laotie-auto-cut）

剪映专业版（JianYing Pro）素材自动剪辑 Skill：给一个素材文件夹，一键生成剪映草稿。
自动收集视频/图片/音频、探测画幅（横/竖屏）、导入主轨、配背景音乐、加动画标题，并自动验证草稿结构。

> 底层能力由 [luoluoluo22/jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill) 提供。

## 功能特性

- **一键成片**：`--assets-dir 素材文件夹 --name 草稿名` 三步出剪映草稿
- **画幅自动匹配**：主视频宽>高→横屏 1920x1080；高>宽→竖屏 1080x1920，防黑边
- **多素材主轨**：视频/图片按文件名排序导入，最多 10 段（可调）
- **BGM 自动铺满**：默认取文件夹第一个音频，时长自动对齐主轨
- **动画标题**：多个标题自动间隔放置、轮换入场动画（复古打字机/向右滑动等）
- **自动验证**：草稿生成后用检查器核对视频轨/音频轨/字幕数量
- **环境自检**：`env_check.py` 检查底层技能、ffmpeg/ffprobe、剪映草稿目录

## 环境要求

| 依赖 | 说明 |
|---|---|
| 剪映专业版（JianYingPro） | Windows 桌面端，草稿目录 `%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft` |
| jianying-editor 技能 | 与本技能放在**同一技能根目录**（见下方安装） |
| Python 3.11+ | 依赖见 jianying-editor 的 `requirements.txt` |
| FFmpeg / ffprobe | 素材探测与归一化必需：`winget install Gyan.FFmpeg` |
| Playwright Chromium（可选） | 网页动效转视频功能用：`playwright install chromium` |

## 安装

```bash
# 1. 底层技能（与本技能同目录）
git clone https://github.com/luoluoluo22/jianying-editor-skill.git
#    文件夹名保持 jianying-editor（或 jianying-editor-skill）

# 2. 本技能：把 laotie-auto-cut/ 文件夹放入同一技能根目录

# 3. Python 依赖 + FFmpeg
cd jianying-editor-skill && pip install -r requirements.txt
winget install Gyan.FFmpeg
```

技能根目录参考：豆包办公 `workspace/.user_skills/`、Claude Code `.claude/skills/` 或 `~/.agents/skills/`、
Cursor/Trae 按 jianying-editor 仓库 README 的安装说明。

## 使用

对 AI 说一句话即可触发，例如：

- 「把 `D:\旅行素材` 快剪成 Vlog，加标题『周末露营记』」
- 「用 `C:\素材` 里的视频做个 30 秒短视频，配个 BGM」

也可以直接命令行运行：

```bash
# 环境检查
python laotie-auto-cut/scripts/env_check.py

# 自动剪辑
python laotie-auto-cut/scripts/auto_edit.py \
  --assets-dir "D:\旅行素材" \
  --name "周末露营记" \
  --titles "周末露营记|感谢观看" \
  --ratio 16:9

# 验证草稿
python laotie-auto-cut/scripts/verify_draft.py --name "周末露营记" --expect-video 1 --expect-audio 1 --expect-text 2
```

**注意**：草稿生成后需重启剪映（或点进旧草稿再退出）才能在列表中看到新草稿。

## 参数一览（auto_edit.py）

| 参数 | 说明 | 默认 |
|---|---|---|
| `--assets-dir` | 素材文件夹（自动收集视频/图片/音频） | - |
| `--video/--image/--audio` | 指定单个素材 | - |
| `--name` | 剪映草稿名（必填） | - |
| `--bgm` | 背景音乐 | 文件夹第一个音频 |
| `--titles` | 标题列表，`\|` 分隔 | 无 |
| `--ratio` | `16:9` / `9:16` | 按主视频自动 |
| `--clip-duration` | 每段素材时长(秒) | 视频自身时长/图片3秒 |
| `--max-clips` | 主轨素材上限 | 10 |
| `--duration` | BGM 时长(秒) | 主轨总时长 |

## 更新

技能为独立文件夹，替换整个 `laotie-auto-cut/` 即可升级；本项目仓库可直接 `git pull`。

## License

MIT（本技能封装层）；底层 jianying-editor 遵循其仓库 LICENSE。
