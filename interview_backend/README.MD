
### 核心框架
- FastAPI：高性能的现代 Python Web 框架
- SQLAlchemy：Python SQL 工具包和 ORM
- OpenCV (cv2)：计算机视觉库
- MediaPipe：Google 的机器学习解决方案库
- Whisper：OpenAI 的语音识别模型
- NumPy：科学计算库
- pyAudioAnalysis：音频特征提取库

### 数据库
- SQLite：轻量级关系型数据库

## 项目结构

```
interview_backend/
├── analyzer/                # 分析器模块
│   ├── analysis/           # 具体分析实现
│   │   ├── video_analyzer.py   # 视频分析
│   │   ├── voice_analyzer.py   # 语音分析
│   │   └── text_analyzer.py    # 文本分析
│   └── models/             # 评分模型
├── main.py                 # 主程序入口
├── config.py              # 配置文件
└── database.py           # 数据库模型
```

## API 接口说明

### 1. 视频上传
```http
POST /api/upload
```
- 功能：上传视频文件
- 请求体：multipart/form-data
- 参数：
  - file: 视频文件（支持格式：webm, mp4）（可选）
  - file: 音频文件（可选）
  - file: 图片文件（可选）
- 返回：
  ```json
  {
      "code": 200,
      "message": "文件上传成功",
      "data": {
        none/"video_url": "string",
        none/"audio_url":"string",
        none/"image_url":"string"
      }
  }
  ```

### 2. 视频分析
```http
POST /api/analyze/video
```
- 功能：分析视频内容
- 请求体：
  ```json
  {
    "video_path": "string",
    "resume_text": "string"
  }
  ```
- 返回：
  ```json
  {
    "code": 200,
    "data": {
      "scores": {
        "total": float,
        "video": float,
        "voice": float,
        "text": float
      },
      "details": {
        "video_data": {
          "posture_stability": float,
          "hand_movement": float,
          "eyebrow_raise": float
        },
        "voice_data": {
          "speech_rate": float,
          "pitch_variation": float,
          "energy_variation": float
        },
        "text_data": {
          "keyword_count": int,
          "content_coherence": float,
          "resume_similarity": float
        }
      },
      "suggestions": "string"
    }
  }
  ```

## 主要功能模块

### 1. VideoAnalyzer
```python
class VideoAnalyzer:
    def analyze_frame(self, frame):
        """分析单帧图像，返回面部表情、姿态等数据"""
```
- 使用 MediaPipe 进行人脸检测和姿态估计
- 分析眉毛运动、姿态稳定性和手部动作
- 返回标准化的评分结果

### 2. VoiceAnalyzer
```python
class VoiceAnalyzer:
    def analyze_audio(self, audio_path):
        """分析音频文件，返回语音特征和文本"""
```
- 使用 Whisper 进行语音识别
- 使用 pyAudioAnalysis 提取音频特征
- 分析语速、音调变化和音量变化

### 3. TextAnalyzer
```python
class TextAnalyzer:
    def analyze(self, text, resume_text=""):
        """分析文本内容，评估表达质量"""
```
- 关键词提取和匹配
- 内容连贯性分析
- 与简历相关性分析

## 配置说明

### 1. 环境变量
在 `config.py` 中配置：
- UPLOAD_DIR：上传文件存储目录
- MAX_FILE_SIZE：最大文件大小限制
- ALLOWED_EXTENSIONS：允许的文件类型

### 2. 模型参数
可在 `analyzer/models/config.py` 中调整：
- 视频分析阈值
- 语音特征权重
- 文本评分参数

## 部署说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 安装额外依赖：
```bash
python -m spacy download zh_core_web_sm
```

3. 启动服务：
```bash
fastapi dev main.py
```

## 注意事项

1. 视频分析要求：
   - 清晰的人脸图像
   - 稳定的光线条件
   - 合适的拍摄角度

2. 音频分析要求：
   - 清晰的语音
   - 较低的背景噪音
   - 合适的音量水平

3. 性能考虑：
   - 视频大小限制：100MB
   - 视频长度建议：2-5分钟
   - 分析过程可能需要一定时间

## 使用说明

1. 录制视频后自动跳转至报告页面
2. 点击"开始分析"按钮进行视频分析
3. 分析完成后自动显示结果
4. 可通过拖动左侧结果层调整查看区域大小
5. 右侧详细报告提供完整的分析数据
