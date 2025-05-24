import whisper
import numpy as np
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import ShortTermFeatures as sF

class VoiceAnalyzer:
    def __init__(self, model_size="base"):
        """
        初始化语音分析器
        model_size: whisper模型大小，可选 "tiny", "base", "small", "medium", "large"
        """
        self.model = whisper.load_model(model_size)
        
    def analyze_audio(self, audio_path):
        """分析音频文件，返回语音特征和文本"""
        # 语音转文本
        text_result = self.model.transcribe(audio_path)
        
        # 提取音频特征
        [Fs, x] = aIO.read_audio_file(audio_path)
        F, f_names = sF.feature_extraction(x, Fs, 0.050*Fs, 0.025*Fs)
        
        # 计算语音特征
        speech_rate = self._calc_speech_rate(text_result["text"], text_result["segments"])
        pitch_stats = self._calc_pitch_stats(F[1])  # 使用第二个特征向量(pitch)
        energy_stats = self._calc_energy_stats(F[0])  # 使用第一个特征向量(energy)
        
        return {
            "text": text_result["text"],
            "speech_rate": speech_rate,  # 语速(字/秒)
            "pitch_variation": pitch_stats["std"],  # 音高变化
            "pitch_mean": pitch_stats["mean"],  # 平均音高
            "energy_mean": energy_stats["mean"],  # 平均音量
            "energy_variation": energy_stats["std"],  # 音量变化
            "segments": text_result["segments"]  # 分段信息
        }
    
    def _calc_speech_rate(self, text, segments):
        """计算语速"""
        if not segments:
            return 0.0
        
        total_chars = len(text)
        total_duration = segments[-1]["end"]
        return total_chars / total_duration if total_duration > 0 else 0
    
    def _calc_pitch_stats(self, pitch_vector):
        """计算音高统计特征"""
        return {
            "mean": float(np.mean(pitch_vector)),
            "std": float(np.std(pitch_vector)),
            "max": float(np.max(pitch_vector)),
            "min": float(np.min(pitch_vector))
        }
    
    def _calc_energy_stats(self, energy_vector):
        """计算音量统计特征"""
        return {
            "mean": float(np.mean(energy_vector)),
            "std": float(np.std(energy_vector)),
            "max": float(np.max(energy_vector)),
            "min": float(np.min(energy_vector))
        } 