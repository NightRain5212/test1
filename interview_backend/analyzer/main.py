import cv2
import numpy as np
import os
from pathlib import Path
import sys
from datetime import datetime
import subprocess
import shutil

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def check_ffmpeg():
    """检查是否安装了ffmpeg"""
    if shutil.which('ffmpeg') is None:
        raise RuntimeError(
            "未找到 ffmpeg。请按照以下步骤安装：\n"
            "Windows：\n"
            "1. 下载 ffmpeg: https://github.com/BtbN/FFmpeg-Builds/releases\n"
            "2. 解压到某个目录（如 C:\\ffmpeg）\n"
            "3. 将 bin 目录（如 C:\\ffmpeg\\bin）添加到系统环境变量 PATH 中\n"
            "4. 重启终端和IDE\n"
            "\n"
            "Linux：\n"
            "sudo apt update && sudo apt install ffmpeg\n"
            "\n"
            "macOS：\n"
            "brew install ffmpeg"
        )

from analysis.video_analyzer import VideoAnalyzer
from analysis.voice_analyzer import VoiceAnalyzer
from analysis.text_analyzer import TextAnalyzer
from models.scorer import InterviewScorer
from models.suggestion_generator import SuggestionGenerator

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))
from config import TEMP_DIR, AUDIO_DIR

class InterviewAnalyzer:
    def __init__(self, resume_text=""):
        """
        初始化面试分析系统
        resume_text: 简历文本
        """
        # 检查 ffmpeg 是否已安装
        check_ffmpeg()
        
        self.video_analyzer = VideoAnalyzer()
        self.voice_analyzer = VoiceAnalyzer(model_size="base")
        self.text_analyzer = TextAnalyzer()
        self.scorer = InterviewScorer()
        self.suggestion_generator = SuggestionGenerator()
        self.resume_text = resume_text
        
        # 设置临时文件存储路径
        self.temp_dir = Path("D:/interview_temp")
        # 确保临时目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_interview(self, video_path):
        """
        分析面试视频
        video_path: 视频文件路径
        """
        try:
            print(f"开始分析视频: {video_path}")
            
            # 读取视频
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
                
            print("视频文件打开成功，开始提取音频...")
            
            # 提取音频
            audio_path = self._extract_audio(video_path)
            print(f"音频提取成功: {audio_path}")
            
            print("开始分析视频帧...")
            # 分析视频帧
            video_results = []
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                result = self.video_analyzer.analyze_frame(frame)
                video_results.append(result)
                frame_count += 1
                if frame_count % 100 == 0:  # 每100帧打印一次进度
                    print(f"已处理 {frame_count} 帧")
            cap.release()
            print(f"视频帧分析完成，共处理 {frame_count} 帧")
            
            # 汇总视频分析结果
            print("正在汇总视频分析结果...")
            video_data = self._aggregate_video_results(video_results)
            
            # 分析音频
            print("开始分析音频...")
            voice_data = self.voice_analyzer.analyze_audio(audio_path)
            print("音频分析完成")
            
            # 分析文本
            print("开始分析文本...")
            text_data = self.text_analyzer.analyze(voice_data["text"], self.resume_text)
            print("文本分析完成")
            
            # 计算综合得分
            print("计算综合得分...")
            score_result = self.scorer.calculate_score(video_data, voice_data, text_data)
            
            # 生成建议
            print("生成分析建议...")
            suggestions = self.suggestion_generator.generate_suggestions(score_result)
            
            # 合并结果
            final_result = {
                **score_result,
                "suggestions": suggestions["raw_response"]
            }
            
            print("分析完成")
            return final_result
            
        except Exception as e:
            print(f"分析过程中出现错误: {str(e)}")
            raise
    
    def _extract_audio(self, video_path):
        """从视频中提取音频"""
        # 确保音频目录存在
        audio_dir = Path(AUDIO_DIR)
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一的音频文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        audio_filename = f"audio_{timestamp}.wav"
        audio_path = audio_dir / audio_filename
        
        try:
            # 使用 ffmpeg 提取音频
            subprocess.run([
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # 不处理视频
                '-acodec', 'pcm_s16le',  # 音频编码
                '-ar', '44100',  # 采样率
                '-ac', '2',  # 声道数
                '-y',  # 覆盖已存在的文件
                str(audio_path)
            ], check=True, capture_output=True)
            
            return str(audio_path)
        except subprocess.CalledProcessError as e:
            print(f"音频提取失败: {e.stderr.decode()}")
            raise ValueError(f"音频提取失败: {str(e)}")
        except Exception as e:
            print(f"音频提取过程出错: {str(e)}")
            raise ValueError(f"音频提取过程出错: {str(e)}")
    
    def _aggregate_video_results(self, results):
        """汇总视频分析结果"""
        if not results:
            return {
                "eyebrow_raise": 0.0,
                "posture_stability": 0.0,
                "hand_movement": 0.0
            }
            
        try:
            # 过滤掉无效的结果
            valid_results = [r for r in results if r is not None]
            
            if not valid_results:
                return {
                    "eyebrow_raise": 0.0,
                    "posture_stability": 0.0,
                    "hand_movement": 0.0
                }
            
            # 计算各指标的平均值
            eyebrow_raises = [float(r.get("eyebrow_raise", 0.0)) for r in valid_results]
            posture_stabilities = [float(r.get("posture_stability", 0.0)) for r in valid_results]
            hand_movements = [float(r.get("hand_movement", 0.0)) for r in valid_results]
            
            # 使用 numpy 的 nan_to_num 来处理可能的 NaN 值
            return {
                "eyebrow_raise": float(np.nan_to_num(np.mean(eyebrow_raises))),
                "posture_stability": float(np.nan_to_num(np.mean(posture_stabilities))),
                "hand_movement": float(np.nan_to_num(np.mean(hand_movements)))
            }
        except Exception as e:
            print(f"汇总视频结果时出错: {str(e)}")
            return {
                "eyebrow_raise": 0.0,
                "posture_stability": 0.0,
                "hand_movement": 0.0
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