# 技术配置（原始提取）

## 步骤 1：资源准备与环境配置

### 步骤定义
获取并预处理开源模型与评测集资源，完成所提方案运行所需的软硬件环境配置

### 参与人员
- 角色名称：算法工程师
- 技能要求：
1. 熟练使用多种思维链策略，对前沿与流行的开/闭源大模型资源较熟悉，有自己的使用经验、使用总结与心得
2. 熟练掌握NLP经典深度学习模型（如Transformer系、LLaMA系、GLM系等）及相关资源（网站、库、博客等）；掌握至少一种常用深度学习开发框架，如PyTorch等；对GPT-3.5之后的大规模生成式语言模型（大模型）的工作原理和最新消息保持持续关注与兴趣
3. 熟练掌握Python语言，会使用基本的正则表达式和命令行脚本；熟知NLP基础概念及经典任务（分类、匹配、序列标注、生成等）；能熟练运用常见NLP开源库（HanLP、LTP、Jieba等）
4. 态度积极主动，沟通有条理，有好奇心与自驱力
- 角色数量：1 人

### 本步输入
- 输入名称：环境配置所需资源
- 输入介绍：
检查运行环境的硬件是否满足下述要求：GPU 最好为 NVIDIA A10 及以上（可选），显存 ≥ 16GB 的 GPU（可选）、CPU ≥8 核、内存 ≥ 16GB，操作系统为 Linux（Ubuntu 20.04+）。
- 输入示例：
请列出清单自检：
NVIDIA A10 及以上（可选）
显存 ≥ 16GB 的GP（可选）U
CPU ≥8 核
内存 ≥ 16GB

### 本步产出
- 输出名称：环境配置所需资源就绪
- 输出介绍：服务器已配置GPU 驱动（可选）、Python 环境、Node 环境，满足模型部署的硬件与系统要求

### 预估时间
1-2 日

## 步骤 2：Claude Code 安装和配置

### 步骤定义
通过 Node 安装和配置 Claude Code

### 参与人员
- 角色名称：前端工程师/后端/算法工程师
- 技能要求：熟悉 node 即可
- 角色数量：1

### 本步输入
- 输入名称：安装和配置 Claude Code
- 输入介绍：基于 Node 环境来安装和配置 Claude Code
- 输入示例：
相关命令如下：
```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 配置环境变量（以 ~/.bashrc 为例，其他如 ~/.zshrc 等同理）
echo 'export ANTHROPIC_BASE_URL="YOUR_BASE_URL"' >> ~/.bashrc
echo 'export ANTHROPIC_AUTH_TOKEN="YOUR_AUTH_TOKEN"' >> ~/.bashrc

# 配置模型
vim ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "YOUR_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "YOUR_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "YOUR_OPUS_MODEL"
  }
}

# 启动成功确认命令，claude 进入命令行，输入任意文字后有收到对应回复且无报错则配置完成
claude
> your_input
```
- 资源链接：
1. Claude Code GitHub：https://github.com/anthropics/claude-code

### 本步产出
- 输出名称：可用的 Claude Code 服务
- 输出介绍：通过 Claude Code 自动调用相关 MCP 服务来完成企业级介绍视频制作

### 预估时间
0.5-1 日

## 步骤 3：ffmpeg-mcp 服务构建、启动

### 步骤定义
构建 ffmpeg-mcp 服务，支持视频压缩、多音轨视频烧录、音视频文件提取等场景视频编辑操作

### 参与人员
- 角色名称：后端/算法工程师
- 技能要求：熟悉 linux 常用命令、shell、ffmpeg 和 python
- 角色数量：1

### 本步输入
- 输入名称：ffmpeg-mcp 服务构建、启动
- 输入介绍：通过安装相关 python 依赖来安装和启动相关 mcp 服务
- 输入示例：
系统层面安装 ffmpeg（以 ubuntu 为例）：
```bash
# 安装
sudo apt update
sudo apt install ffmpeg

# 验证
ffmpeg -version

注：也可以通过 Homebrew 安装
```
requirements.txt 如下：
```bash
# 建议 python 3.10 及以上版本，如 python 3.11

# 核心依赖
loguru>=0.7.0
python-dotenv>=1.0.0
mcp>=1.0.0

# FFmpeg 相关依赖
ffmpeg-python>=0.2.0

# 注：通过 pip install -r requirements.txt 来安装
```
python代码如下：
```python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

import ffmpeg
from loguru import logger
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

env_name = 'dev'
logger.remove()
log_level = 'INFO'
filename = os.path.basename(__file__)
log_dir = os.path.join('logs', env_name, filename.split('.')[0])
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, '{time:YYYY-MM-DD}.log')
logger.add(sys.stderr, level=log_level)
logger.add(log_file, level=log_level, rotation="00:00", enqueue=True, serialize=False, encoding="utf-8")

app = FastMCP("video-ffmpeg-tools", host='0.0.0.0', port=int(os.getenv("PORT")))


class VideoError(Exception):
pass


def get_video_duration(video_path: str) -> float:
"""
获取视频文件的时长

:param video_path: 视频文件路径
:return: 视频时长（秒）
"""
logger.info(f"Getting video duration: {video_path}")

if not os.path.exists(video_path):
raise VideoError(f"视频文件不存在: {video_path}")

try:
probe = ffmpeg.probe(video_path)
duration = float(probe['format']['duration'])
logger.info(f"Video duration: {duration} seconds")
return duration
except Exception as e:
logger.error(f"Failed to get video duration: {str(e)}")
raise VideoError(f"获取视频时长失败: {str(e)}")


def extract_audio(video_path: str, output_path: str) -> str:
"""
从视频文件中提取音频

:param video_path: 输入视频文件路径
:param output_path: 输出音频文件路径
:return: 输出音频文件路径
"""
logger.info(f"Extracting audio from {video_path} to {output_path}")

if not os.path.exists(video_path):
raise VideoError(f"视频文件不存在: {video_path}")

# 确保输出目录存在
output_dir = os.path.dirname(output_path)
if output_dir and not os.path.exists(output_dir):
os.makedirs(output_dir, exist_ok=True)

try:
ffmpeg.input(video_path).output(
output_path,
acodec='pcm_s16le',
ar='44100',
ac=2
).run(overwrite_output=True)

if not os.path.exists(output_path):
raise VideoError(f"音频文件提取失败: {output_path}")

logger.info(f"Audio extraction completed: {output_path}")
return output_path
except Exception as e:
logger.error(f"Audio extraction failed: {str(e)}")
raise VideoError(f"音频提取失败: {str(e)}")


def extract_video(video_path: str, output_path: str) -> str:
"""
从视频文件中提取视频流（无音频）

:param video_path: 输入视频文件路径
:param output_path: 输出视频文件路径
:return: 输出视频文件路径
"""
logger.info(f"Extracting video from {video_path} to {output_path}")

if not os.path.exists(video_path):
raise VideoError(f"视频文件不存在: {video_path}")

# 确保输出目录存在
output_dir = os.path.dirname(output_path)
if output_dir and not os.path.exists(output_dir):
os.makedirs(output_dir, exist_ok=True)

try:
(
ffmpeg
.input(video_path)
.output(output_path, **{'an': None, 'c:v': 'copy'})
.run(overwrite_output=True)
)

if not os.path.exists(output_path):
raise VideoError(f"视频文件提取失败: {output_path}")

logger.info(f"Video extraction completed: {output_path}")
return output_path
except Exception as e:
logger.error(f"Video extraction failed: {str(e)}")
raise VideoError(f"视频提取失败: {str(e)}")


def speed_up_video(video_path: str, output_path: str, speed_factor: float) -> str:
"""
加快视频播放速度

:param video_path: 输入视频文件路径
:param output_path: 输出视频文件路径
:param speed_factor: 速度倍数
:return: 输出视频文件路径
"""
logger.info(f"Speeding up video {video_path} by factor {speed_factor}")

if not os.path.exists(video_path):
raise VideoError(f"视频文件不存在: {video_path}")

if speed_factor <= 0:
raise VideoError("速度倍数必须大于0")

# 确保输出目录存在
output_dir = os.path.dirname(output_path)
if output_dir and not os.path.exists(output_dir):
os.makedirs(output_dir, exist_ok=True)

# 删除已存在的输出文件
if os.path.exists(output_path):
os.remove(output_path)

try:
# 计算视频时间戳倍数
video_pts_factor = 1.0 / speed_factor

# 构建FFmpeg命令
cmd = [
'ffmpeg',
'-i', video_path,
'-filter:v', f'setpts={video_pts_factor}*PTS',
'-filter:a', f'atempo={speed_factor}',
output_path
]

logger.info(f"Executing command: {' '.join(cmd)}")

# 执行命令
subprocess.run(cmd, check=True)

if not os.path.exists(output_path):
raise VideoError(f"视频速度处理失败: {output_path}")

logger.info(f"Video speed up completed: {output_path}")
return output_path
except subprocess.CalledProcessError as e:
logger.error(f"FFmpeg command failed with return code {e.returncode}")
raise VideoError(f"视频速度处理失败: FFmpeg命令执行错误")
except Exception as e:
logger.error(f"Video speed up failed: {str(e)}")
raise VideoError(f"视频速度处理失败: {str(e)}")


def get_audio_duration(audio_path: str) -> float:
"""
获取音频文件的时长

:param audio_path: 音频文件路径
:return: 音频时长（秒）
"""
logger.info(f"Getting audio duration: {audio_path}")

if not os.path.exists(audio_path):
raise VideoError(f"音频文件不存在: {audio_path}")

try:
probe = ffmpeg.probe(audio_path)
duration = float(probe['format']['duration'])
logger.info(f"Audio duration: {duration} seconds")
return duration
except Exception as e:
logger.error(f"Failed to get audio duration: {str(e)}")
raise VideoError(f"获取音频时长失败: {str(e)}")


def generate_silence(input_audio_path: str, duration: float, output_path: str = None) -> str:
"""
生成与输入音频同参数的静音音频

:param input_audio_path: 参考音频文件路径
:param duration: 静音音频时长（秒）
:param output_path: 输出文件路径（可选）
:return: 输出静音音频文件路径
"""
logger.info(f"Generating silence audio based on {input_audio_path}")

if not os.path.exists(input_audio_path):
raise VideoError(f"参考音频文件不存在: {input_audio_path}")

if duration <= 0:
raise VideoError("时长必须大于0")

if not output_path:
output_path = f"silence_{duration}s.wav"

# 确保输出目录存在
output_dir = os.path.dirname(output_path)
if output_dir and not os.path.exists(output_dir):
os.makedirs(output_dir, exist_ok=True)

try:
# 获取参考音频的参数
probe = ffmpeg.probe(input_audio_path)
audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

if not audio_stream:
raise VideoError("无法找到音频流信息")

sample_rate = int(audio_stream['sample_rate'])
channels = int(audio_stream['channels'])

# 确定声道布局
channel_layout = "mono"
if channels == 2:
channel_layout = "stereo"
elif channels > 2:
channel_layout = "multi"

logger.info(f"Generating {duration}s silence with {sample_rate}Hz, {channels} channels")

# 生成静音音频
(
ffmpeg
.input(f'anullsrc=r={sample_rate}:cl={channel_layout}', f='lavfi')
.output(
output_path,
t=duration,
acodec='pcm_s16le',
ar=sample_rate,
ac=channels
)
.run(overwrite_output=True)
)

if not os.path.exists(output_path):
raise VideoError(f"静音音频生成失败: {output_path}")

logger.info(f"Silence audio generated: {output_path}")
return output_path
except Exception as e:
logger.error(f"Silence generation failed: {str(e)}")
raise VideoError(f"静音音频生成失败: {str(e)}")


def merge_multi_track_video(
video_path: str,
audio1_path: str,
audio2_path: str,
subtitle_path: str = None,
output_path: str = None,
audio1_weight: float = 1.0,
audio2_weight: float = 0.05
) -> str:
"""
创建多音轨视频，混合两个音频并添加字幕

:param video_path: 视频文件路径（无音频）
:param audio1_path: 主音频文件路径
:param audio2_path: 背景音频文件路径
:param subtitle_path: 字幕文件路径（可选）
:param output_path: 输出视频文件路径（可选）
:param audio1_weight: 主音频权重
:param audio2_weight: 背景音频权重
:return: 输出视频文件路径
"""
logger.info(f"Merging multi-track video with {audio1_path} and {audio2_path}")

# 检查输入文件
for file_path, file_name in [(video_path, "视频"), (audio1_path, "主音频"), (audio2_path, "背景音频")]:
if not os.path.exists(file_path):
raise VideoError(f"{file_name}文件不存在: {file_path}")

if subtitle_path and not os.path.exists(subtitle_path):
raise VideoError(f"字幕文件不存在: {subtitle_path}")

if not output_path:
output_path = "output_multi_track.mov"

# 确保输出目录存在
output_dir = os.path.dirname(output_path)
if output_dir and not os.path.exists(output_dir):
os.makedirs(output_dir, exist_ok=True)

try:
# 输入文件
video_input = ffmpeg.input(video_path)
audio1_input = ffmpeg.input(audio1_path)
audio2_input = ffmpeg.input(audio2_path)

# 混合音频
mixed_audio = ffmpeg.filter(
[audio1_input, audio2_input],
'amix',
inputs=2,
duration='first',
weights=f'{audio1_weight} {audio2_weight}'
)

# 添加字幕（如果有）
video_stream = video_input.video
if subtitle_path:
video_stream = video_stream.filter('subtitles', subtitle_path)

# 组合视频和混合音频
output = ffmpeg.output(
video_stream,
mixed_audio,
output_path,
vcodec='libx264',
crf=18,
preset='fast',
acodec='aac',
audio_bitrate='192k'
)

# 执行命令
ffmpeg.run(output, overwrite_output=True)

if not os.path.exists(output_path):
raise VideoError(f"多音轨视频生成失败: {output_path}")

logger.info(f"Multi-track video generated: {output_path}")
return output_path
except Exception as e:
logger.error(f"Multi-track video merging failed: {str(e)}")
raise VideoError(f"多音轨视频生成失败: {str(e)}")


# MCP Tools
@app.tool()
def get_video_file_duration(video_path: str) -> float:
"""
获取视频文件的时长

:param video_path: 视频文件的绝对路径
:return: 视频时长（秒）
"""
logger.info(f"Getting video file duration: {video_path}")

try:
duration = get_video_duration(video_path)
logger.info(f"Video duration retrieved successfully: {duration} seconds")
return duration
except Exception as e:
logger.error(f"Failed to get video duration: {str(e)}")
raise VideoError(f"获取视频文件时长失败: {str(e)}")


@app.tool()
def extract_audio_from_video(video_path: str, output_path: str) -> str:
"""
从视频文件中提取音频

:param video_path: 输入视频文件的绝对路径
:param output_path: 输出音频文件的绝对路径
:return: 提取的音频文件路径
"""
logger.info(f"Extracting audio from video: {video_path}")

try:
result_path = extract_audio(video_path, output_path)
logger.info(f"Audio extraction completed: {result_path}")
return result_path
except Exception as e:
logger.error(f"Audio extraction failed: {str(e)}")
raise VideoError(f"从视频提取音频失败: {str(e)}")


@app.tool()
def extract_video_stream(video_path: str, output_path: str) -> str:
"""
从视频文件中提取视频流（无音频）

:param video_path: 输入视频文件的绝对路径
:param output_path: 输出视频文件的绝对路径
:return: 提取的视频文件路径
"""
logger.info(f"Extracting video stream from: {video_path}")

try:
result_path = extract_video(video_path, output_path)
logger.info(f"Video stream extraction completed: {result_path}")
return result_path
except Exception as e:
logger.error(f"Video stream extraction failed: {str(e)}")
raise VideoError(f"从视频提取视频流失败: {str(e)}")


@app.tool()
def compress_video_duration(video_path: str, output_path: str, speed_factor: float) -> str:
"""
通过加速来压缩视频时长

:param video_path: 输入视频文件的绝对路径
:param output_path: 输出视频文件的绝对路径
:param speed_factor: 速度倍数（大于1表示加速）
:return: 处理后的视频文件路径
"""
logger.info(f"Compressing video duration with speed factor {speed_factor}")

try:
result_path = speed_up_video(video_path, output_path, speed_factor)
logger.info(f"Video duration compression completed: {result_path}")
return result_path
except Exception as e:
logger.error(f"Video duration compression failed: {str(e)}")
raise VideoError(f"视频时长压缩失败: {str(e)}")


@app.tool()
def get_audio_file_duration(audio_path: str) -> float:
"""
获取音频文件的时长

:param audio_path: 音频文件的绝对路径
:return: 音频时长（秒）
"""
logger.info(f"Getting audio file duration: {audio_path}")

try:
duration = get_audio_duration(audio_path)
logger.info(f"Audio duration retrieved successfully: {duration} seconds")
return duration
except Exception as e:
logger.error(f"Failed to get audio duration: {str(e)}")
raise VideoError(f"获取音频文件时长失败: {str(e)}")


@app.tool()
def generate_silence_audio(input_audio_path: str, duration: float, output_path: str = None) -> str:
"""
生成与输入音频同参数的静音音频

:param input_audio_path: 参考音频文件的绝对路径
:param duration: 静音音频时长（秒）
:param output_path: 输出静音音频文件的绝对路径
:return: 生成的静音音频文件路径
"""
logger.info(f"Generating silence audio based on: {input_audio_path}")

try:
result_path = generate_silence(input_audio_path, duration, output_path)
logger.info(f"Silence audio generation completed: {result_path}")
return result_path
except Exception as e:
logger.error(f"Silence audio generation failed: {str(e)}")
raise VideoError(f"生成静音音频失败: {str(e)}")


@app.tool()
def create_multi_track_video(
video_path: str,
audio1_path: str,
audio2_path: str,
subtitle_path: str = None,
output_path: str = None,
audio1_weight: float = 1.0,
audio2_weight: float = 0.05
) -> str:
"""
创建多音轨视频，混合两个音频并添加字幕

:param video_path: 视频文件的绝对路径（无音频）
:param audio1_path: 主音频文件的绝对路径
:param audio2_path: 背景音频文件的绝对路径
:param subtitle_path: 字幕文件的绝对路径
:param output_path: 输出视频文件的绝对路径
:param audio1_weight: 主音频权重
:param audio2_weight: 背景音频权重
:return: 生成的多音轨视频文件路径
"""
logger.info(f"Creating multi-track video with: {audio1_path}, {audio2_path}")

try:
result_path = merge_multi_track_video(
video_path, audio1_path, audio2_path, subtitle_path,
output_path, audio1_weight, audio2_weight
)
logger.info(f"Multi-track video creation completed: {result_path}")
return result_path
except Exception as e:
logger.error(f"Multi-track video creation failed: {str(e)}")
raise VideoError(f"创建多音轨视频失败: {str(e)}")


if __name__ == '__main__':
transport = "sse"
app.run(transport=transport)
```
启动命令如下：
```bash
# 前面的 python 代码保存为 server.py，安装后相关依赖后可直接启动
python server.py

注：看到类似"Uvicorn running on http://0.0.0.0:4008 (Press CTRL+C to quit)"则启动成功
```
- 资源链接：
1. mcp-python-sdk GitHub：https://github.com/modelcontextprotocol/python-sdk
2. ffmpeg 官方：https://www.ffmpeg.org/
3. ffmpeg GitHub：https://github.com/FFmpeg/FFmpeg
4. ffmpeg-python GitHub：https://github.com/kkroening/ffmpeg-python
5. loguru GitHub：https://github.com/Delgan/loguru

### 本步产出
- 输出名称：可调用的 ffmpeg-mcp 服务
- 输出介绍：构建和启动 SSE 协议的 ffmpeg-mcp 服务

### 预估时间
0.5-1 日

## 步骤 4：funasr-mcp 服务构建、启动

### 步骤定义
构建 funasr-mcp 服务，支持语音识别，将 wav 等格式的音频文件转写为标准的 srt 字幕文件

### 参与人员
- 角色名称：算法工程师
- 技能要求：
1. 熟练使用多种思维链策略，对前沿与流行的开/闭源大模型资源较熟悉，有自己的使用经验、使用总结与心得
2. 熟练掌握NLP经典深度学习模型（如Transformer系、LLaMA系、GLM系等）及相关资源（网站、库、博客等）；掌握至少一种常用深度学习开发框架，如PyTorch等；对GPT-3.5之后的大规模生成式语言模型（大模型）的工作原理和最新消息保持持续关注与兴趣
3. 熟练掌握Python语言，会使用基本的正则表达式和命令行脚本；熟知NLP基础概念及经典任务（分类、匹配、序列标注、生成等）；能熟练运用常见NLP开源库（HanLP、LTP、Jieba等）
4. 态度积极主动，沟通有条理，有好奇心与自驱力
- 角色数量：1 人

### 本步输入
- 输入名称：funasr-mcp 服务构建、启动
- 输入介绍：通过安装相关 python 依赖来安装和启动相关 mcp 服务
- 输入示例：
requirements.txt 如下：
```bash
# 建议 python 3.10 及以上版本，如 python 3.10

# 核心依赖
loguru>=0.7.0
python-dotenv>=1.0.0
mcp>=1.0.0

# FunASR 相关依赖
torch
torchaudio
funasr
modelscope

# 注：通过 pip install -r requirements.txt 来安装，其中 torch、torchaudio 可以参考 https://pytorch.org/get-started/locally 来安装
```
python代码如下：
```python
# -*- coding: utf-8 -*-
import os
import sys

from funasr import AutoModel
from loguru import logger
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

env_name = 'dev'
logger.remove()
log_level = 'INFO'
filename = os.path.basename(__file__)
log_dir = os.path.join('logs', env_name, filename.split('.')[0])
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, '{time:YYYY-MM-DD}.log')
logger.add(sys.stderr, level=log_level)
logger.add(log_file, level=log_level, rotation="00:00", enqueue=True, serialize=False, encoding="utf-8")

model = AutoModel(
# 语音识别: paraformer-zh, paraformer-en(without timestamp).
model="paraformer-zh",
# 语音端点检测，实时
vad_model="fsmn-vad",
# 标点恢复
punc_model="ct-punc-c",
# 说话人确认/分割. paraformer-zh.
spk_model="cam++",
)

app = FastMCP("asr-funasr-tools", host='0.0.0.0', port=int(os.getenv("PORT")))


class ASRError(Exception):
pass


def format_seconds(seconds: float) -> str:
"""
将秒数转换为小时、分钟、秒和毫秒的格式化字符串。

参数:
seconds (float): 秒数。

返回:
str: 格式化后的时间字符串。
"""
hours = int(seconds // 3600)
minutes = int((seconds % 3600) // 60)
secs = int(seconds % 60)
millis = int((seconds - int(seconds)) * 1000)

return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def audio2result(audio_path: str, hotword: str = "魔搭"):
"""
使用 FunASR 进行语音识别

:param audio_path: 音频文件路径
:param hotword: 热词，默认为"魔搭"
:return: 识别结果
"""
logger.info(f"Processing audio file: {audio_path}")
logger.info(f"Using hotword: {hotword}")

if not os.path.exists(audio_path):
raise ASRError(f"音频文件不存在: {audio_path}")

try:
res = model.generate(
input=audio_path,
batch_size_s=300,
hotword=hotword
)
logger.info(f"Recognition completed, got {len(res)} results")
return res
except Exception as e:
logger.error(f"ASR processing failed: {str(e)}")
raise ASRError(f"语音识别处理失败: {str(e)}")


@app.tool()
def audio2srt_text(audio_path: str, hotword: str = "魔搭") -> str:
"""
将音频文件转换为 SRT 格式的字幕文本

:param audio_path: 音频文件路径（支持 wav、mp3 等格式）
:param hotword: 热词，用于提高特定词汇的识别准确率，默认为"魔搭"
:return: SRT 格式的字幕文本
"""
logger.info(f"Converting audio to SRT: {audio_path}")

try:
result = audio2result(audio_path, hotword)
if not result or not result[0].get('sentence_info'):
raise ASRError("未能获取有效的识别结果")

srt_tex_list = []
sentence_info = result[0].get('sentence_info')

for index, segment in enumerate(sentence_info):
start_time = format_seconds(segment.get('start') / 1000.0)
end_time = format_seconds(segment.get('end') / 1000.0)
text = segment.get('text') or ''
srt_tex = f'{index + 1}\n{start_time} --> {end_time}\n{text}\n'
srt_tex_list.append(srt_tex)

srt_text = '\n'.join(srt_tex_list)
logger.info(f"SRT conversion completed, generated {len(srt_tex_list)} subtitle segments")
return srt_text
except Exception as e:
logger.error(f"SRT conversion failed: {str(e)}")
raise ASRError(f"SRT 转换失败: {str(e)}")


if __name__ == '__main__':
transport = "sse"
app.run(transport=transport)
```
启动命令如下：
```bash
# 前面的 python 代码保存为 server.py，安装后相关依赖后可直接启动
python server.py

注：看到类似"Uvicorn running on http://0.0.0.0:4005 (Press CTRL+C to quit)"则启动成功
```
- 资源链接：
1. mcp-python-sdk GitHub：https://github.com/modelcontextprotocol/python-sdk
2. funasr GitHub：https://github.com/modelscope/FunASR
3. loguru GitHub：https://github.com/Delgan/loguru

### 本步产出
- 输出名称：可调用的 funasr-mcp 服务
- 输出介绍：构建和启动 SSE 协议的 funasr-mcp 服务

### 预估时间
0.5-1 日

## 步骤 5：paddle-speech-tts-mcp 服务构建、启动

### 步骤定义
构建 paddle-speech-tts-mcp 服务，支持 TTS，将文字转为音频文件

### 参与人员
- 角色名称：算法工程师
- 技能要求：
1. 熟练使用多种思维链策略，对前沿与流行的开/闭源大模型资源较熟悉，有自己的使用经验、使用总结与心得
2. 熟练掌握NLP经典深度学习模型（如Transformer系、LLaMA系、GLM系等）及相关资源（网站、库、博客等）；掌握至少一种常用深度学习开发框架，如PyTorch等；对GPT-3.5之后的大规模生成式语言模型（大模型）的工作原理和最新消息保持持续关注与兴趣
3. 熟练掌握Python语言，会使用基本的正则表达式和命令行脚本；熟知NLP基础概念及经典任务（分类、匹配、序列标注、生成等）；能熟练运用常见NLP开源库（HanLP、LTP、Jieba等）
4. 态度积极主动，沟通有条理，有好奇心与自驱力
- 角色数量：1 人

### 本步输入
- 输入名称：paddle-speech-tts-mcp 服务构建、启动
- 输入介绍：通过安装相关 python 依赖来安装和启动相关 mcp 服务
- 输入示例：
requirements.txt 如下：
```bash
# 建议 python 3.10 及以上版本，如 python 3.11

# 核心依赖
loguru>=0.7.0
python-dotenv>=1.0.0
mcp>=1.0.0

# PaddleSpeech 相关依赖
paddlepaddle
pytest-runner
paddlespeech

# 注：通过 pip install -r requirements.txt 来安装，其中 paddlepaddle 可以参考 https://www.paddlepaddle.org.cn/install/quick 来安装
```
python代码如下：
```python
# -*- coding: utf-8 -*-
import os
import sys

from paddlespeech.cli.tts.infer import TTSExecutor
from loguru import logger
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

env_name = 'dev'
logger.remove()
log_level = 'INFO'
filename = os.path.basename(__file__)
log_dir = os.path.join('logs', env_name, filename.split('.')[0])
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, '{time:YYYY-MM-DD}.log')
logger.add(sys.stderr, level=log_level)
logger.add(log_file, level=log_level, rotation="00:00", enqueue=True, serialize=False, encoding="utf-8")

tts = TTSExecutor()

app = FastMCP("tts-paddle-speech-tools", host='0.0.0.0', port=int(os.getenv("PORT")))


class TTSError(Exception):
pass


def text2speech(text: str, output_path: str) -> str:
"""
使用 PaddleSpeech 进行文本转语音

:param text: 要转换的文本
:param output_path: 输出音频文件路径（必填，必须是包含文件名的绝对路径）
:return: 生成的音频文件绝对路径
"""
logger.info(f"Converting text to speech: {text}")

if not text or not text.strip():
raise TTSError("输入文本不能为空")

if not output_path or not output_path.strip():
raise TTSError("输出路径不能为空，请提供有效的输出文件路径")

if not os.path.isabs(output_path):
raise TTSError("输出路径必须是绝对路径，请提供完整的文件路径（如：/path/to/output.wav）")

# 检查是否包含文件名
filename = os.path.basename(output_path)
if not filename:
raise TTSError("输出路径必须包含文件名，请提供完整的文件路径（如：/path/to/output.wav）")

# 检查文件扩展名
valid_extensions = ['.wav', '.mp3', '.flac', '.aac', '.m4a']
file_ext = os.path.splitext(filename)[1].lower()
if not file_ext:
raise TTSError("输出文件必须包含扩展名，支持格式：.wav, .mp3, .flac, .aac, .m4a")
if file_ext not in valid_extensions:
raise TTSError(f"不支持的文件格式：{file_ext}，支持格式：.wav, .mp3, .flac, .aac, .m4a")

# 确保输出目录存在
output_dir = os.path.dirname(output_path)
if output_dir and not os.path.exists(output_dir):
os.makedirs(output_dir, exist_ok=True)

try:
tts(text=text.strip(), output=output_path)

if not os.path.exists(output_path):
raise TTSError(f"语音文件生成失败: {output_path}")

logger.info(f"TTS conversion completed: {output_path}")
return output_path
except Exception as e:
logger.error(f"TTS processing failed: {str(e)}")
raise TTSError(f"文本转语音处理失败: {str(e)}")


@app.tool()
def text_to_speech(text: str, output_path: str) -> str:
"""
将文本转换为语音文件

:param text: 要转换的文本内容
:param output_path: 输出音频文件路径（必填，必须是包含文件名的绝对路径）
:return: 生成的音频文件的绝对路径
"""
logger.info(f"Text to speech conversion request: {text[:50]}...")

try:
result_path = text2speech(text, output_path)
logger.info(f"Text to speech conversion completed: {result_path}")
return result_path
except Exception as e:
logger.error(f"Text to speech conversion failed: {str(e)}")
raise TTSError(f"文本转语音失败: {str(e)}")


if __name__ == '__main__':
transport = "sse"
app.run(transport=transport)
```
启动命令如下：
```bash
# 前面的 python 代码保存为 server.py，安装后相关依赖后可直接启动
python server.py

注：看到类似"Uvicorn running on http://0.0.0.0:4006 (Press CTRL+C to quit)"则启动成功
```
- 资源链接：
1. mcp-python-sdk GitHub：https://github.com/modelcontextprotocol/python-sdk
2. paddle-speech GitHub：https://github.com/PaddlePaddle/PaddleSpeech
3. loguru GitHub：https://github.com/Delgan/loguru

### 本步产出
- 输出名称：可调用的 paddle-speech-tts-mcp 服务
- 输出介绍：构建和启动 SSE 协议的 paddle-speech-tts-mcp 服务

### 预估时间
0.5-1 日

## 步骤 6：视频压缩倍数计算 mcp 服务构建、启动

### 步骤定义
构建自定义 mcp 服务视频压缩倍数计算（记作 cus-tool-video_compression_calculator），用于计算多个视频的压缩时长分配，确保压缩后的总时长不超过目标时长

### 参与人员
- 角色名称：后端/算法工程师
- 技能要求：熟悉 python 即可
- 角色数量：1

### 本步输入
- 输入名称：视频压缩倍数计算 mcp 服务构建、启动
- 输入介绍：通过安装相关 python 依赖来安装和启动相关 mcp 服务
- 输入示例：
requirements.txt 如下：
```bash
# 建议 python 3.10 及以上版本，如 python 3.11

loguru>=0.7.0
python-dotenv>=1.0.0
mcp>=1.0.0

# 注：通过 pip install -r requirements.txt 来安装
```
python版本代码如下：
```python
# -*- coding: utf-8 -*-
import os
import sys
from typing import List, Tuple, Dict, Any
from loguru import logger
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

env_name = 'dev'
logger.remove()
log_level = 'INFO'
filename = os.path.basename(__file__)
log_dir = os.path.join('logs', env_name, filename.split('.')[0])
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, '{time:YYYY-MM-DD}.log')
logger.add(sys.stderr, level=log_level)
logger.add(log_file, level=log_level, rotation="00:00", enqueue=True, serialize=False, encoding="utf-8")

app = FastMCP("video-compression-calculator-tools", host='0.0.0.0', port=int(os.getenv("PORT")))


class VideoCompressionError(Exception):
pass


def calculate_video_compression(
key: float,
step_list: List[float],
key_range_target: List[float],
count_target: float = 60.0
) -> Tuple[float, List[float], float, float, List[float]]:
"""
计算视频压缩时长分配 - 严格满足总时长约束，同时追求压缩倍率一致性

核心算法：
1. 尝试统一压缩倍率
2. 如果key视频超出范围，将其固定在边界
3. 剩余时间严格分配给其他视频，确保总和=count_target

:param key: Key视频原始时长
:param step_list: 其他视频时长的列表
:param key_range_target: Key视频压缩后的允许范围 [最小值, 最大值]
:param count_target: 目标总时长
:return: 压缩后的key时长、其他视频时长列表、总时长、key压缩倍率、其他视频压缩倍率列表
"""
logger.info(f"Calculating video compression: key={key}, steps={step_list}, range={key_range_target}, target={count_target}")

# 参数验证
if key <= 0:
raise VideoCompressionError("Key视频时长必须大于0")
if not step_list or any(s <= 0 for s in step_list):
raise VideoCompressionError("Step视频列表不能为空且所有时长必须大于0")
if len(key_range_target) != 2 or key_range_target[0] >= key_range_target[1]:
raise VideoCompressionError("Key视频约束范围无效，需要[最小值, 最大值]且最小值小于最大值")
if count_target <= 0:
raise VideoCompressionError("目标总时长必须大于0")

try:
# 计算总时长
step_total = sum(step_list)
total_original = key + step_total

if total_original == 0:
return 0, [], 0, 1.0, []

# key视频的约束范围
k_min, k_max = key_range_target

# 修正：处理key约束范围
# 1. 如果原始key小于k_min，压缩后应该使用k_min（相当于延长）
# 2. 如果原始key大于k_max，压缩后最多只能是原始时长
# 3. 正常情况下，压缩后不能超过原始时长

# 确定实际可用的约束范围
actual_k_min = k_min # 最小值保持不变，可以延长视频
actual_k_max = min(k_max, key) if key > k_min else k_max # 最大值不能超过原始时长

# 但如果原始key < k_min，我们需要特殊处理
if key < k_min:
# 原始时长小于最小约束，必须延长到至少k_min
actual_k_min = k_min
actual_k_max = max(k_min, min(k_max, count_target - step_total * 0.5)) # 确保其他视频至少有0.5秒
else:
# 原始时长大于等于最小约束，正常压缩
actual_k_min = min(k_min, key)
actual_k_max = min(k_max, key)

# 方案1：尝试统一压缩倍率
uniform_ratio = count_target / total_original
key_uniform = key * uniform_ratio

# 根据key_uniform的情况选择策略
if actual_k_min <= key_uniform <= actual_k_max:
# 理想情况：统一压缩倍率
key_compress = key_uniform
elif key_uniform < actual_k_min:
# key视频压缩后太短，固定在最小值
key_compress = actual_k_min
else: # key_uniform > actual_k_max
# key视频压缩后太长，固定在最大值
key_compress = actual_k_max

# 计算剩余时间
remaining_time = count_target - key_compress

# 严格分配剩余时间给step videos
if step_total > 0 and remaining_time > 0:
# 按原始比例分配剩余时间
step_ratio = remaining_time / step_total
step_list_compress = []

# 首先按比例分配
for i, duration in enumerate(step_list):
compressed = duration * step_ratio
# 确保每个视频至少0.5秒
compressed = max(0.5, compressed)
step_list_compress.append(compressed)

# 检查是否因为最小值限制导致总和不等于remaining_time
current_step_sum = sum(step_list_compress)

if abs(current_step_sum - remaining_time) > 0.001: # 允许小误差
if current_step_sum > remaining_time:
# 需要减少一些时长
excess = current_step_sum - remaining_time

# 从最长的视频开始减少，但保持最小0.5秒
sorted_indices = sorted(range(len(step_list_compress)),
key=lambda i: step_list_compress[i],
reverse=True)

for idx in sorted_indices:
if excess <= 0.001:
break
available = step_list_compress[idx] - 0.5
if available > 0:
reduction = min(available, excess)
step_list_compress[idx] -= reduction
excess -= reduction

# 如果还有剩余（极端情况），可能需要调整key
if excess > 0.001:
# 尝试减少key_compress，但不能低于actual_k_min
available_key_reduction = key_compress - actual_k_min
if available_key_reduction > 0:
reduction = min(available_key_reduction, excess)
key_compress -= reduction
remaining_time = count_target - key_compress
# 重新计算step_list_compress
step_ratio = remaining_time / step_total
step_list_compress = [max(0.5, duration * step_ratio)
for duration in step_list]

else: # current_step_sum < remaining_time
# 需要增加一些时长，按比例分配到所有视频
deficit = remaining_time - current_step_sum
for i in range(len(step_list_compress)):
step_list_compress[i] += deficit * (step_list[i] / step_total)

# 最终微调确保总和精确等于count_target
current_total = key_compress + sum(step_list_compress)
if abs(current_total - count_target) > 0.001:
# 调整最长的step视频
adjustment = count_target - current_total
if step_list_compress:
max_idx = step_list_compress.index(max(step_list_compress))
step_list_compress[max_idx] += adjustment

elif remaining_time <= 0:
# 特殊情况：key_compress已经占满或超过目标时长
if key_compress >= count_target:
key_compress = min(key_compress, count_target)
step_list_compress = []
else:
# 剩余时间很少，平均分配给每个视频0.5秒
step_list_compress = [0.5] * len(step_list)
total_step = sum(step_list_compress)
if key_compress + total_step > count_target:
key_compress = count_target - total_step
else:
step_list_compress = []

# 计算压缩倍率
key_compression_ratio = key_compress / key if key > 0 else 1.0
step_compression_ratios = [
compressed / original if original > 0 else 1.0
for compressed, original in zip(step_list_compress, step_list)
]

# 最终总时长（应该正好等于count_target）
count_compress = key_compress + sum(step_list_compress)

# 验证总和
assert abs(count_compress - count_target) < 0.01, \
f"总时长{count_compress:.2f}不等于目标{count_target}"

logger.info(f"Video compression calculation completed successfully")
return key_compress, step_list_compress, count_compress, key_compression_ratio, step_compression_ratios

except AssertionError as e:
logger.error(f"Calculation assertion failed: {str(e)}")
raise VideoCompressionError(f"计算验证失败: {str(e)}")
except Exception as e:
logger.error(f"Video compression calculation failed: {str(e)}")
raise VideoCompressionError(f"视频压缩计算失败: {str(e)}")


@app.tool()
def video_compression_calculator(
key: float,
step_list: List[float],
key_range_target: List[float],
count_target: float = 60.0
) -> Dict[str, Any]:
"""
视频压缩时长计算器 - MCP工具接口

========== 功能说明 ==========
用于计算多个视频的压缩时长分配，确保压缩后的总时长不超过目标时长。
主要应用于教学视频或演示视频的场景，其中包含：
- 展示效果部分（前10-15秒）：需要重点展示
- 步骤讲解部分：安装配置步骤的简要说明

========== 输入参数详细说明 ==========

key: float
- 参数含义：展示效果视频的原始时长（秒）
- 取值范围：大于0的浮点数
- 示例值：15.0 (表示15秒的展示效果视频)
- 约束：必须大于0
- 说明：这个视频通常放在最前面，用于展示软件或功能的效果

step_list: List[float]
- 参数含义：其余各个讲解视频的原始时长列表（秒）
- 取值范围：每个元素都是大于0的浮点数
- 示例值：[30.0, 45.0, 20.0] (表示3个讲解视频，分别是30秒、45秒、20秒)
- 约束：列表不能为空，所有时长必须大于0
- 说明：这些视频通常包含安装、配置、操作步骤等讲解内容

key_range_target: List[float]
- 参数含义：展示效果视频压缩后的期望时长范围 [最小值, 最大值]
- 取值范围：[最小值, 最大值]，且最小值 < 最大值
- 示例值：[10.0, 15.0] (表示希望展示效果视频压缩后在10-15秒之间)
- 约束：必须包含2个元素的列表，第一个元素小于第二个元素
- 说明：用于控制展示效果部分的最终时长，确保足够的展示时间

count_target: float (可选参数，默认值: 60.0)
- 参数含义：所有视频压缩后的目标总时长（秒）
- 取值范围：大于0的浮点数
- 示例值：60.0 (表示希望最终总时长为60秒)
- 约束：必须大于0
- 说明：这是整个视频组合的目标总时长，算法会确保压缩后的总时长接近这个值

========== 返回值详细说明 ==========

返回一个包含以下字段的字典：

key_original: float
- 含义：展示效果视频的原始时长
- 单位：秒

step_list_original: List[float]
- 含义：讲解视频的原始时长列表
- 单位：秒

key_compressed: float
- 含义：展示效果视频压缩后的时长
- 单位：秒
- 特点：保证在 key_range_target 范围内或接近该范围

step_list_compressed: List[float]
- 含义：讲解视频压缩后的时长列表
- 单位：秒
- 特点：按比例分配剩余时间，每个视频至少0.5秒

total_original: float
- 含义：所有视频的原始总时长
- 单位：秒

total_compressed: float
- 含义：所有视频压缩后的实际总时长
- 单位：秒
- 特点：应该接近或等于 count_target

target_total: float
- 含义：目标总时长（即输入的 count_target）
- 单位：秒

key_compression_ratio: float
- 含义：展示效果视频的压缩倍率
- 计算方式：key_compressed / key_original
- 说明：大于1表示延长，小于1表示压缩

step_compression_ratios: List[float]
- 含义：讲解视频的压缩倍率列表
- 计算方式：step_compressed / step_original
- 说明：每个元素对应一个视频的压缩倍率

key_range_target: List[float]
- 含义：展示效果视频的目标时长范围
- 单位：秒

calculation_successful: bool
- 含义：计算是否成功
- 取值：True 表示成功，False 表示失败

========== 使用示例 ==========

示例1：标准使用
video_compression_calculator(
key=15.0, # 展示效果视频15秒
step_list=[30.0, 45.0], # 两个讲解视频，分别30秒和45秒
key_range_target=[10.0, 15.0], # 希望展示效果在10-15秒之间
count_target=60.0 # 总时长控制在60秒
)

========== 算法特点 ==========
1. 优先保持展示效果视频在指定范围内
2. 严格保证总时长接近目标值
3. 按比例分配剩余时间给讲解视频
4. 确保每个视频至少0.5秒的基本时长
5. 返回详细的压缩信息便于分析

:param key: Key视频原始时长
:param step_list: 其他视频时长的列表
:param key_range_target: Key视频压缩后的允许范围 [最小值, 最大值]
:param count_target: 目标总时长
:return: 包含压缩结果详细信息的字典
"""
logger.info(f"Video compression calculator request: key={key}, target={count_target}")

try:
result = calculate_video_compression(key, step_list, key_range_target, count_target)

key_compress, step_list_compress, count_compress, key_compression_ratio, step_compression_ratios = result

return {
"key_original": key,
"step_list_original": step_list,
"key_compressed": key_compress,
"step_list_compressed": step_list_compress,
"total_original": key + sum(step_list),
"total_compressed": count_compress,
"target_total": count_target,
"key_compression_ratio": key_compression_ratio,
"step_compression_ratios": step_compression_ratios,
"key_range_target": key_range_target,
"calculation_successful": True
}
except Exception as e:
logger.error(f"Video compression calculator failed: {str(e)}")
raise VideoCompressionError(f"视频压缩计算失败: {str(e)}")


if __name__ == '__main__':
transport = "sse"
app.run(transport=transport)
```
启动命令如下：
```bash
# 前面的 python 代码保存为 server.py，安装后相关依赖后可直接启动
python server.py

注：看到类似"Uvicorn running on http://0.0.0.0:4007 (Press CTRL+C to quit)"则启动成功
```
- 资源链接：
1. mcp-python-sdk GitHub：https://github.com/modelcontextprotocol/python-sdk
2. loguru GitHub：https://github.com/Delgan/loguru

### 本步产出
- 输出名称：可调用的视频压缩倍数计算 mcp 服务
- 输出介绍：构建和启动 SSE 协议的视频压缩倍数计算 mcp 服务

### 预估时间
0.25-0.5 日

## 步骤 7：song-generation 服务配置、启动（可选）

### 步骤定义
配置启动 song-generation 服务，支持文本生成纯音乐（记作 bgm.wav）
注：当前步骤需要 GPU，且配置有一定门槛，也可以通过 https://suno.com/ 等在线产品来使用

### 参与人员
- 角色名称：算法工程师
- 技能要求：
1. 熟练使用多种思维链策略，对前沿与流行的开/闭源大模型资源较熟悉，有自己的使用经验、使用总结与心得
2. 熟练掌握NLP经典深度学习模型（如Transformer系、LLaMA系、GLM系等）及相关资源（网站、库、博客等）；掌握至少一种常用深度学习开发框架，如PyTorch等；对GPT-3.5之后的大规模生成式语言模型（大模型）的工作原理和最新消息保持持续关注与兴趣
3. 熟练掌握Python语言，会使用基本的正则表达式和命令行脚本；熟知NLP基础概念及经典任务（分类、匹配、序列标注、生成等）；能熟练运用常见NLP开源库（HanLP、LTP、Jieba等）
4. 态度积极主动，沟通有条理，有好奇心与自驱力
- 角色数量：1 人

### 本步输入
- 输入名称：song-generation 服务配置、启动
- 输入介绍：通过安装相关 python 依赖来安装和启动相关网页服务
- 输入示例：
相关命令如下：
```bash
# 拉取 docker 镜像（确保网络通畅），并启动服务进入容器
docker pull juhayna/song-generation-levo:hf0613
docker run -it --gpus all --network=host juhayna/song-generation-levo:hf0613 /bin/bash

# 下载必要资源
huggingface-cli download lglg666/SongGeneration-Runtime --local-dir ./runtime
mv runtime/ckpt ckpt
mv runtime/third_party third_party

# 下载相关模型
# download SongGeneration-base
huggingface-cli download lglg666/SongGeneration-base --local-dir ./songgeneration_base
# download SongGeneration-base-new
huggingface-cli download lglg666/SongGeneration-base-new --local-dir ./songgeneration_base_new
# download SongGeneration-base-full
huggingface-cli download lglg666/SongGeneration-base-full --local-dir ./songgeneration_base_full
# download SongGeneration-large
huggingface-cli download lglg666/SongGeneration-large --local-dir ./songgeneration_large

# 启动网页服务
bash tools/gradio/run.sh your_ckpt_path

注：启动后，在浏览器中访问 http://IP:8081，在左侧文本框输入文字，再点击下方按钮生成歌曲/纯音乐（生成后可播放和下载对应音频文件）
```
- 资源链接：
1. SongGeneration GitHub：https://github.com/tencent-ailab/SongGeneration

### 本步产出
- 输出名称：可使用的 song-generation 网页服务
- 输出介绍：配置和启动 gradio song-generation 网页服务

### 预估时间
1-2 日

## 步骤 8：使用 Claude Code 生成介绍视频

### 步骤定义
使用 Claude Code 自动调用前面的几个 MCP 服务来生成介绍视频

### 参与人员
- 角色名称：算法工程师
- 技能要求：
1. 熟练使用多种思维链策略，对前沿与流行的开/闭源大模型资源较熟悉，有自己的使用经验、使用总结与心得
2. 熟练掌握NLP经典深度学习模型（如Transformer系、LLaMA系、GLM系等）及相关资源（网站、库、博客等）；掌握至少一种常用深度学习开发框架，如PyTorch等；对GPT-3.5之后的大规模生成式语言模型（大模型）的工作原理和最新消息保持持续关注与兴趣
3. 熟练掌握Python语言，会使用基本的正则表达式和命令行脚本；熟知NLP基础概念及经典任务（分类、匹配、序列标注、生成等）；能熟练运用常见NLP开源库（HanLP、LTP、Jieba等）
4. 态度积极主动，沟通有条理，有好奇心与自驱力
- 角色数量：1 人

### 本步输入
- 输入名称：使用 Claude Code 生成介绍视频
- 输入介绍：和 Claude Code 交互确认输入信息来生成介绍视频
- 输入示例：
先在 Claude Code 里面注册前面步骤构建和启动的 MCP 服务
```bash
# ASR
claude mcp add -s user -t sse asr-funasr http://127.0.0.1:4005/sse

# TTS
claude mcp add -s user -t sse tts-paddle_speech http://127.0.0.1:4006/sse

# Custom Tools
claude mcp add -s user -t sse cus-tool-video_compression_calculator http://127.0.0.1:4007/sse

# Video
claude mcp add -s user -t sse video-ffmpeg http://127.0.0.1:4008/sse
```
传入已有视频素材和 video_editing_skill.md
```python
# 视频素材要求如下
项目根目录/
├── files/ # 原始素材文件夹
│ ├── number.title.suffix # 不同功能的录屏视频文件 (必须)
│ ├── text.txt # 文本/文案素材文件 (必须)
│ └── bgm.wav # 背景音乐 (可选)
└── video_editing_skill.md # 视频生成流程文档 (必须)


# video_editing_skill.md 内容如下
# 企业级介绍视频制作标准流程

## 概述

本文档提供了一套完整的企业级介绍视频制作标准化流程，基于MCP工具链实现从原始视频素材到精简成品视频的全自动化处理。

### 核心设计原则

- **TTS时长优先**: 先生成TTS音频，视频压缩时长适配TTS
- **严格文本校对**: 确保字幕与原始文本高度一致
- **音画同步保证**: 确保音频、视频、字幕完美同步
- **用户确认机制**: 关键参数需用户确认
- **并行处理优化**: 提升整体处理效率

## 输入要求

### 文件结构

```
项目根目录/
├── files/ # 原始素材文件夹
│ ├── number.title.suffix # 不同功能的录屏视频文件 (必须)
│ ├── text.txt # 文本素材文件 (必须)
│ └── bgm.wav # 背景音乐 (可选)（存在则必须用上）
└── video_editing_skill.md # 本流程文档
```

### 文件规范

#### 文本素材文件 (files/text.txt)

- **格式**: UTF-8编码的.txt文件
- **内容结构**: 按视频序号分段，每段对应一个视频文件
- **格式要求**:

```txt
# 1
接下来我们来看一下构建流程，新建工作流，导入之前准备好的工作流，点击保存就好了。
# 2
我们来添加模型，点击左边的模型再点击右上角的添加模型。我们选择这个接口格式，这边我们用的是第三方代理，点击保存就可以了。好，到这里，模型配置就完成了。
```

**要求**:

- 文字内容与视频画面内容匹配
- 语言表达简洁流畅，适合口语化表达
- 无特殊字符和复杂格式

#### 视频文件 (files/number-title.suffix)

- **格式**: .mov, .mp4, .avi, .mkv
- **命名**: `{序号}.{描述}.mov`
- **要求**: 画面清晰，内容完整，音频清晰可识别

#### 背景音乐 (files/bgm.wav) - 可选

- **格式**: .wav, .mp3, .m4a
- **要求**: 时长 ≥ 最终视频时长，音质良好无噪音

## 技术参数

```yaml
视频处理:
输出编码: H.264
输出格式: MP4
帧率: 30fps
质量: CRF 23
音频处理:
采样率: 24000Hz
声道: 单声道
格式: WAV
字幕格式:
编码: UTF-8
格式: SRT
同步精度: ±0.1秒
文本处理:
编码: UTF-8
校对精度: 字符级匹配
容错率: < 0.1%
```

## 完整执行流程

### 阶段1: 环境准备

创建输出目录结构：`processed/{audio,video,srt,final}`

### 阶段2: 输入文件验证

1. 验证必需文件存在：`files/text.txt` 和视频文件
2. 解析文本素材，提取段落内容
3. 验证文本段落数与视频文件数量匹配

### 阶段3: 视频内容分析与用户确认

1. 获取所有视频的时长信息
2. 智能识别关键视频段（文件名包含"效果展示"、"demo"、"演示"等关键词或时长最长）
3. 用户确认关键参数：
- 目标总时长（60秒/90秒/120秒）
- 关键内容视频文件
- 关键内容位置（开头/中间/结尾）

### 阶段4: TTS音频生成与时长计算

#### 4.1 TTS音频生成

生成自然时长的TTS音频：

1. 按段落分割文本内容
2. 逐段生成TTS音频到 `processed/audio/audio-tts-*.wav`（使用自然语速，不预设时长）
3. 获取每个TTS音频的实际时长
4. 记录文本内容与TTS实际时长的对应关系

#### 4.2 视频压缩时长计算

调用"视频压缩时长计算器 - MCP工具接口"确定最终压缩参数：

1. 输入所有TTS音频的实际时长
2. 输入原始视频的时长信息
3. 根据目标总时长，智能分配各视频段的压缩时长
4. 生成压缩时长配置文件，用于后续视频压缩

### 阶段5: 视频/音频分离

并行执行以下任务：

1. 从原始视频中提取音频到 `processed/audio/audio-original-*.wav`
2. 提取无声视频流到 `processed/video/video-silent-*.mov`

### 阶段6: 时长匹配压缩

基于阶段4.2计算的压缩时长配置执行视频压缩：

1. 读取压缩时长配置文件
2. 获取原始视频时长
3. 计算压缩倍率 = 原始时长 / 目标时长
4. 应用压缩倍率压缩视频到 `processed/video/video-compressed-*.mov`
5. 验证压缩后时长与配置一致（这一步很重要，必须要调用 MCP 工具来验证！），容差在±0.1秒内

### 阶段7: 字幕生成

基于TTS音频重新生成字幕：

1. 为每个TTS音频文件生成ASR字幕
2. 保存字幕到 `processed/srt/srt-tts-*.srt`
3. 提取字幕文本内容

### 阶段8: 文本校对

严格校对ASR字幕与原始文本的一致性：

1. 计算原文与字幕文本的相似度
2. 相似度 >= 95%视为通过
3. 相似度 < 95%则生成校对报告，要求人工校对
4. 人工校对后保存到 `processed/srt/srt-manual-*.srt`
5. 确定最终使用的字幕文件

### 阶段9: 视频段合成

为每个视频段合成完整的音画字幕：

1. 生成静音音频作为第二音轨
2. 将压缩视频、TTS音频、字幕合成为完整视频段
3. 验证音画同步性（时长差异 < 0.1秒）
4. 保存到 `processed/video/video-synthesized-*.mp4`
注：这一步必须调用 ffmpeg 相关 mcp 工具

### 阶段10: 视频合并

根据用户确认的关键内容位置重新排序：

1. 根据用户偏好调整视频段顺序（关键内容可置前）
2. 创建合并列表文件
3. 按顺序合并所有视频段为最终视频
4. 保存到 `processed/final/final_video_no_bgm.mp4`

### 阶段11: 背景音乐添加

如存在背景音乐文件，并行生成多个版本：

1. 无背景音乐版本
2. 5%背景音乐版本
3. 15%背景音乐版本

## 最终交付物

### 输出文件结构

```
processed/
├── final/ # 最终视频文件
│ ├── final_video_no_bgm.mp4 # 无背景音乐版本
│ ├── final_video_with_bgm_5.mp4 # 5%背景音乐版本
│ └── final_video_with_bgm_15.mp4 # 15%背景音乐版本
├── audio/ # 音频文件
│ ├── audio-original-*.wav # 原始音频
│ └── audio-tts-*.wav # TTS音频
├── video/ # 视频文件
│ ├── video-silent-*.mov # 无声视频
│ ├── video-compressed-*.mov # 压缩视频
│ └── video-synthesized-*.mp4 # 合成视频段
├── srt/ # 字幕文件
│ ├── srt-tts-*.srt # 基于TTS生成的字幕
│ ├── srt-final-*.srt # 验证通过的最终字幕
│ └── srt-manual-*.srt # 人工校对的字幕
└── text/ # 文本文件
├── verification_report.txt # 文本校对报告
├── sync_issues.txt # 同步问题报告
└── compression_config.json # 视频压缩时长配置
```

### 质量标准

- **总时长**: 符合确认的目标时长
- **音视频同步**: 严格同步，差异 < 0.1秒
- **文本准确性**: 与原文档95%以上相似度
- **字幕同步**: 基于TTS音频生成，时间轴精确匹配
- **关键内容**: 根据用户偏好放置（推荐开头）
```
在项目根目录启动 Claude Code 来生成介绍视频
```bash
# 较高权限启动 claude，请确保项目根目录下除了 files 和 video_editing_skill.md 无其他文件，并且禁止使用 "rm -rf *" 等危险指令
claude --dangerously-skip-permissions
> 根据视频素材和video_editing_skill.md生成介绍视频

注：前面会有视频时长等需要用户确认的选项，后面会自动生成最终介绍视频（生成效果和使用的大模型及ASR、TTS 模型等效果相关，且大模型具有一定随机性）
```
- 资源链接：
1. Claude Code GitHub：https://github.com/anthropics/claude-code

### 本步产出
- 输出名称：介绍视频
- 输出介绍：Claude Code 自动剪辑的最终介绍视频

### 预估时间
0.5-1 日
