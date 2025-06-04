
### 2.1 核心类

#### InterviewAnalyzer
- 位置：`main.py`
- 功能：系统的主要入口类，协调各个分析器的工作
- 主要方法：
  - `__init__(resume_text="")`: 初始化分析器
  - `analyze_interview(video_path)`: 执行完整的面试分析
  - `_extract_audio(video_path)`: 从视频中提取音频
  - `_aggregate_video_results(results)`: 汇总视频分析结果

### 2.2 分析器模块（analysis目录）

#### VideoAnalyzer
- 位置：`analysis/video_analyzer.py`
- 功能：分析视频中的面部表情、姿态稳定性和手部动作
- 关键指标：
  - 眉毛抬起（eyebrow_raise）
  - 姿态稳定性（posture_stability）
  - 手部动作（hand_movement）

#### VoiceAnalyzer
- 位置：`analysis/voice_analyzer.py`
- 功能：分析语音特征，包括语速、语调等
- 特点：支持不同大小的模型选择（base/large）

#### TextAnalyzer
- 位置：`analysis/text_analyzer.py`
- 功能：分析面试内容与简历的相关性，评估回答质量

### 2.3 模型模块（models目录）

#### InterviewScorer
- 位置：`models/scorer.py`
- 功能：根据各维度分析结果计算综合得分

#### SuggestionGenerator
- 位置：`models/suggestion_generator.py`
- 功能：基于分析结果生成改进建议

## 3. 技术特点

1. **多模态分析**：
   - 视频分析：面部表情、姿态识别
   - 语音分析：语音转文字、语音特征提取
   - 文本分析：内容相关性、答案质量评估

2. **音视频处理**：
   - 使用OpenCV (`cv2`) 处理视频流
   - 使用ffmpeg提取音频
   - 支持多种视频格式

3. **数据处理**：
   - 使用NumPy进行数值计算
   - 实时视频帧分析
   - 结果聚合与统计

## 4. 使用方法

```python
# 创建分析器实例
analyzer = InterviewAnalyzer(resume_text="简历文本")

# 分析面试视频
result = analyzer.analyze_interview("视频文件路径")

# 获取分析结果
print(f"总分: {result['scores']['total']}")
print(f"视频表现: {result['scores']['video']}")
print(f"语音表现: {result['scores']['voice']}")
print(f"内容表现: {result['scores']['text']}")
print("建议:", result["suggestions"])
```

## 5. 输出结果格式

```python
{
    "scores": {
        "total": float,      # 总分
        "video": float,      # 视频表现分数
        "voice": float,      # 语音表现分数
        "text": float        # 内容表现分数
    },
    "suggestions": str       # AI面试官的评价与建议
}
```

## 6. 依赖要求

- Python 3.x
- OpenCV (cv2)
- NumPy
- ffmpeg（用于音频提取）

## 7. 注意事项

1. 使用前确保系统已安装ffmpeg
2. 视频文件需要有效且可访问
3. 建议提供详细的简历文本以获得更准确的分析结果
