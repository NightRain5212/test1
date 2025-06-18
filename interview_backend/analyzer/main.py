import cv2
import numpy as np
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import subprocess
import shutil
from typing import Dict, Any

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from config import TEMP_DIR, AUDIO_DIR, VIDEO_DIR, SPARK_CONFIG
from .analysis.video_analyzer import VideoAnalyzer
from .analysis.voice_analyzer import VoiceAnalyzer
from .analysis.text_analyzer import TextAnalyzer
from .models.scorer import InterviewScorer
from .models.suggestion_generator import SuggestionGenerator
from spark_client import SparkClient

def check_ffmpeg():
    """检查是否安装了ffmpeg"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return True
    except FileNotFoundError:
        return False

class InterviewAnalyzer:
    def __init__(self, resume_text=""):
        """
        初始化面试分析系统
        resume_text: 简历文本
        """
        # 检查 ffmpeg 是否已安装
        if not check_ffmpeg():
            raise RuntimeError("请先安装ffmpeg")
        
        # 检查并创建必要的目录
        for dir_path in [TEMP_DIR, AUDIO_DIR, VIDEO_DIR]:
            os.makedirs(dir_path, exist_ok=True)
        
        self.video_analyzer = VideoAnalyzer()
        self.voice_analyzer = VoiceAnalyzer()
        self.text_analyzer = TextAnalyzer()
        self.scorer = InterviewScorer()
        self.suggestion_generator = SuggestionGenerator()
        self.spark_client = SparkClient()
        self.resume_text = resume_text
        self.interview_questions = []
        self.current_question_index = 0
        
        # 设置临时文件存储路径
        self.temp_dir = Path(TEMP_DIR)
        # 确保临时目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    async def process_resume(self, resume_text, job_type):
        """
        处理简历并生成面试问题
        resume_text: 简历文本
        job_type: 职位类型（如：前端、后端、算法等）
        """
        self.resume_text = resume_text
        
        # 生成面试问题提示词
        prompt = f"""
        作为专业的面试官，请根据以下简历和职位类型生成3个专业的面试问题。
        问题应该包括：
        1. 1个关于简历中具体项目或经验的深入性问题
        2. 1个关于{job_type}岗位必备的技术问题
        3. 1个关于职业规划或开放性问题

        简历内容：
        {resume_text}

        职位类型：{job_type}

        请按以下格式返回问题列表：
        1. [问题1]
        2. [问题2]
        3. [问题3]
        """
        
        try:
            # 调用SparkClient生成问题
            response = await self.spark_client.chat(prompt)
            
            # 解析返回的问题列表
            questions = []
            for line in response.split('\n'):
                if line.strip() and line[0].isdigit():
                    question = line.split('.', 1)[1].strip()
                    if question:
                        questions.append(question)
            
            # 如果没有成功生成问题，使用默认问题
            if not questions:
                questions = [
                    f"请介绍一下您在{job_type}方面的工作经验。",
                    f"您认为{job_type}最重要的技能是什么？您是如何掌握这些技能的？",
                    "您能描述一下您参与过的最有挑战性的项目吗？"
                ]
            
            self.interview_questions = questions
            self.current_question_index = 0
            
            return questions
            
        except Exception as e:
            print(f"生成面试问题时出错: {str(e)}")
            # 返回默认问题
            default_questions = [
                f"请介绍一下您在{job_type}方面的工作经验。",
                f"您认为{job_type}最重要的技能是什么？您是如何掌握这些技能的？",
                "您能描述一下您参与过的最有挑战性的项目吗？"
            ]
            self.interview_questions = default_questions
            self.current_question_index = 0
            return default_questions

    def get_next_question(self):
        """获取下一个面试问题"""
        if self.current_question_index < len(self.interview_questions):
            question = self.interview_questions[self.current_question_index]
            self.current_question_index += 1
            return question
        return None

    def is_interview_complete(self):
        """检查面试是否完成所有问题"""
        return self.current_question_index >= len(self.interview_questions)

    async def analyze(self, video_path: str, job_type: str) -> Dict[str, Any]:
        """分析面试视频并生成报告"""
        try:
            # 并行执行视频、语音和文本分析
            video_task = asyncio.create_task(self.video_analyzer.analyze(video_path))
            voice_task = asyncio.create_task(self.voice_analyzer.analyze(video_path))
            text_task = asyncio.create_task(self.text_analyzer.analyze(video_path))

            # 等待所有分析完成
            video_analysis, voice_analysis, text_analysis = await asyncio.gather(
                video_task, voice_task, text_task
            )

            # 使用星火大模型生成分析报告
            analysis_result = await self.spark_client.analyze_interview(
                video_analysis,
                voice_analysis,
                text_analysis,
                job_type
            )

            return {
                "success": True,
                "data": {
                    "video_analysis": video_analysis,
                    "voice_analysis": voice_analysis,
                    "text_analysis": text_analysis,
                    "analysis_result": analysis_result
                }
            }

        except Exception as e:
            print(f"分析过程出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def run(self, video_path=None, audio_path=None, text=None):
        """
        运行面试分析
        :param video_path: 视频文件路径
        :param audio_path: 音频文件路径
        :param text: 文本内容
        :return: 分析结果
        """
        try:
            # 并行执行分析任务
            tasks = []
            if video_path:
                tasks.append(self.video_analyzer.analyze(video_path))
            if audio_path:
                tasks.append(self.voice_analyzer.analyze(audio_path))
            if text:
                tasks.append(self.text_analyzer.analyze(text, self.resume_text))
                
            # 等待所有分析完成
            results = await asyncio.gather(*tasks)
            
            # 整合分析结果
            video_result = results[0] if video_path else None
            voice_result = results[1] if audio_path else None
            text_result = results[2] if text else None
            
            # 计算总分
            total_score = self.scorer.calculate_total_score(
                video_result=video_result,
                voice_result=voice_result,
                text_result=text_result
            )
            
            # 生成建议
            suggestions = self.suggestion_generator.generate_suggestions(
                video_result=video_result,
                voice_result=voice_result,
                text_result=text_result
            )
            
            # 使用星火大模型进行综合评估
            analysis_result = await self.spark_client.analyze_interview(
                video_path=video_path,
                audio_path=audio_path,
                text=text
            )
            
            return {
                "status": "success",
                "data": {
                    "total_score": total_score,
                    "video_analysis": video_result,
                    "voice_analysis": voice_result,
                    "text_analysis": text_result,
                    "suggestions": suggestions,
                    "ai_analysis": analysis_result
                }
            }
            
        except Exception as e:
            print(f"分析过程出错: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

# 测试
def run(target_video="interview_video.mp4"):
    """测试函数"""
    analyzer = InterviewAnalyzer()
    asyncio.run(analyzer.run(video_path=target_video))

if __name__ == "__main__":
    run() 