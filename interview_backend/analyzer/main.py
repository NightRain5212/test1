import cv2
import numpy as np
from analysis.video_analyzer import VideoAnalyzer
from analysis.voice_analyzer import VoiceAnalyzer
from analysis.text_analyzer import TextAnalyzer
from models.scorer import InterviewScorer
from models.suggestion_generator import SuggestionGenerator

class InterviewAnalyzer:
    def __init__(self, resume_text=""):
        """
        初始化面试分析系统
        resume_text: 简历文本
        """
        self.video_analyzer = VideoAnalyzer()
        self.voice_analyzer = VoiceAnalyzer(model_size="base")
        self.text_analyzer = TextAnalyzer()
        self.scorer = InterviewScorer()
        self.suggestion_generator = SuggestionGenerator()
        self.resume_text = resume_text
        
    def analyze_interview(self, video_path):
        """
        分析面试视频
        video_path: 视频文件路径
        """
        # 读取视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
            
        # 提取音频
        audio_path = self._extract_audio(video_path)
        
        # 分析视频帧
        video_results = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            result = self.video_analyzer.analyze_frame(frame)
            video_results.append(result)
        cap.release()
        
        # 汇总视频分析结果
        video_data = self._aggregate_video_results(video_results)
        
        # 分析音频
        voice_data = self.voice_analyzer.analyze_audio(audio_path)
        
        # 分析文本
        text_data = self.text_analyzer.analyze(voice_data["text"], self.resume_text)
        
        # 计算综合得分
        score_result = self.scorer.calculate_score(video_data, voice_data, text_data)
        
        # 生成建议
        suggestions = self.suggestion_generator.generate_suggestions(score_result)
        
        # 合并结果
        final_result = {
            **score_result,
            "suggestions": suggestions["raw_response"]
        }
        
        return final_result
    
    def _extract_audio(self, video_path):
        """从视频中提取音频"""
        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        # 使用ffmpeg提取音频
        import subprocess
        command = [
            "ffmpeg", "-i", video_path,
            "-ac", "1", "-ar", "16000",
            "-loglevel", "error",
            audio_path
        ]
        subprocess.run(command, check=True)
        return audio_path
    
    def _aggregate_video_results(self, results):
        """汇总视频分析结果"""
        if not results:
            return None
            
        # 计算各指标的平均值
        eyebrow_raises = [r["eyebrow_raise"] for r in results]
        posture_stabilities = [r["posture_stability"] for r in results]
        hand_movements = [r["hand_movement"] for r in results]
        
        return {
            "eyebrow_raise": float(np.mean(eyebrow_raises)),
            "posture_stability": float(np.mean(posture_stabilities)),
            "hand_movement": float(np.mean(hand_movements))
        }

# 测试
def run():
    # 示例用法
    resume_text = """
    我是一名有5年经验的Python开发工程师，
    擅长Web开发和数据分析。
    曾负责过多个大型项目的架构设计和开发工作。
    """
    
    analyzer = InterviewAnalyzer(resume_text)
    
    try:
        result = analyzer.analyze_interview("interview_video.mp4")
        print("\n=== 面试分析结果 ===")
        print(f"总分: {result['scores']['total']:.2f}")
        print("\n=== 分项得分 ===")
        print(f"视频表现: {result['scores']['video']:.2f}")
        print(f"语音表现: {result['scores']['voice']:.2f}")
        print(f"内容表现: {result['scores']['text']:.2f}")
        
        print("\n=== AI面试官评价与建议 ===")
        print(result["suggestions"])
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")

if __name__ == "__main__":
    run() 