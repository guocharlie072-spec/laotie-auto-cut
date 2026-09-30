# jianying-editor 常用 API 摘要

本技能通过 `jianying-editor`（同 `.user_skills` 目录兄弟技能）的 `scripts/jy_wrapper.py` 提供剪辑能力。
脚本 bootstrap 模板：

```python
import os, sys
# 定位 jianying-editor 技能根（含 scripts/jy_wrapper.py），加入 sys.path 后：
# from jy_wrapper import JyProject
```

## JyProject 常用方法

| 方法 | 说明 |
|---|---|
| `JyProject(name, overwrite=True, width=1920, height=1080)` | 创建工程；竖屏传 `width=1080, height=1920`；`overwrite=True` 覆盖同名草稿并自动修复损坏草稿 |
| `add_media_safe(path, start_time=None, duration=None, track_name=None)` | 导入素材（自动识别视频/图片/音频）；`start_time=None` 表示智能追加到轨道末尾；返回片段对象 |
| `add_audio_safe(path, ...)` | 音频专用别名，确保进音频轨 |
| `add_text_simple(text, start_time="1s", duration="3s", anim_in="复古打字机")` | 加文字/标题，可带入场动画；同轨文字勿重叠 |
| `add_narrated_subtitles(text, speaker="zh_female_xiaopengyou")` | 一键“文案→TTS 配音→轨道对齐→字幕” |
| `add_cloud_media(name_or_id, start_time, duration)` | 从剪映云端素材库导入（需先 `build_cloud_music_library.py` 挖掘曲库） |
| `save()` | 保存草稿（**必须调用**，同时触发剪映侧刷新） |

## 配套 CLI（jianying-editor/scripts/）

- `draft_inspector.py summary --name <草稿名>`：查看草稿结构（轨道/片段/素材统计）
- `asset_search.py "关键词" -c filters`：按名搜索剪映特效/转场/滤镜
- `auto_exporter.py <草稿名> <输出.mp4> --res 1080 --fps 60`：自动导出（仅 Windows，剪映 5.9- 最稳）
- `api_validator.py`：环境诊断

## 关键约束

- 项目分辨率必须与主素材比例一致，否则黑边。
- 素材入库前会经 ffmpeg 归一化（非标准尺寸/编码时自动转码为 H.264+yuv420p）。
- 脚本（业务代码）放用户项目目录，不要写进技能目录，便于技能 git 更新。
- 剪映草稿默认目录：`%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft`（macOS: `~/Movies/JianyingPro/...`）。
- 自动导出期间勿动鼠标键盘；导出后剪映列表需重启或进出草稿刷新。
