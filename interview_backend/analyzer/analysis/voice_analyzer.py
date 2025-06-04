import whisper
import numpy as np
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import ShortTermFeatures as sF
import os

class VoiceAnalyzer:
    def __init__(self, model_size="base"):
        """
        初始化语音分析器
        model_size: whisper模型大小，可选 "tiny", "base", "small", "medium", "large"
        """
        try:
            self.model = whisper.load_model(model_size)
            self.model_size = model_size
        except Exception as e:
            print(f"加载Whisper模型失败: {str(e)}")
            self.model = None
            
    def analyze_audio(self, audio_path):
        """分析音频文件，返回语音特征和文本"""
        try:
            if not os.path.exists(audio_path):
                raise ValueError(f"音频文件不存在: {audio_path}")
                
            # 语音转文本
            if self.model is None:
                raise ValueError("Whisper模型未正确加载")
                
            text_result = self.model.transcribe(audio_path)
            
            try:
                # 提取音频特征
                [Fs, x] = aIO.read_audio_file(audio_path)
                if len(x.shape) > 1:  # 如果是立体声，转换为单声道
                    x = np.mean(x, axis=1)
                    
                # 确保音频数据是连续的
                x = np.ascontiguousarray(x)
                
                # 计算帧长和步长（以样本数为单位）
                frame_length = int(0.050 * Fs)  # 50ms
                frame_step = int(0.025 * Fs)    # 25ms
                
                # 特征提取
                F, f_names = sF.feature_extraction(x, Fs, frame_length, frame_step)
                
                # 确保特征向量有足够的数据
                if F.shape[1] < 10:  # 如果帧数太少
                    F = np.pad(F, ((0, 0), (0, 10 - F.shape[1])), mode='constant')
                
            except Exception as e:
                print(f"音频特征提取失败: {str(e)}")
                # 返回默认的音频特征
                return self._get_default_result(text_result.get("text", ""))
            
            # 计算语音特征
            try:
                speech_rate = self._calc_speech_rate(text_result["text"], text_result.get("segments", []))
                pitch_stats = self._calc_pitch_stats(F[1] if F.shape[0] > 1 else np.zeros(F.shape[1]))
                energy_stats = self._calc_energy_stats(F[0] if F.shape[0] > 0 else np.zeros(F.shape[1]))
            except Exception as e:
                print(f"特征计算失败: {str(e)}")
                return self._get_default_result(text_result.get("text", ""))
            
            return {
                "text": text_result.get("text", ""),
                "speech_rate": float(speech_rate),
                "pitch_variation": float(pitch_stats["std"]),
                "pitch_mean": float(pitch_stats["mean"]),
                "energy_mean": float(energy_stats["mean"]),
                "energy_variation": float(energy_stats["std"]),
                "segments": text_result.get("segments", []),
                "volume": float(np.mean(np.abs(x))) if len(x) > 0 else 0.0
            }
            
        except Exception as e:
            print(f"音频分析失败: {str(e)}")
            return self._get_default_result("")
    
    def _get_default_result(self, text=""):
        """返回默认的分析结果"""
        return {
            "text": text,
            "speech_rate": 0.0,
            "pitch_variation": 0.0,
            "pitch_mean": 0.0,
            "energy_mean": 0.0,
            "energy_variation": 0.0,
            "segments": [],
            "volume": 0.0
        }
    
    def _calc_speech_rate(self, text, segments):
        """计算语速"""
        try:
            if not text or not segments:
                return 0.0
            
            total_chars = len(text)
            total_duration = segments[-1]["end"] if segments else 0
            return float(total_chars / total_duration) if total_duration > 0 else 0.0
        except Exception as e:
            print(f"语速计算错误: {str(e)}")
            return 0.0
    
    def _calc_pitch_stats(self, pitch_vector):
        """计算音高统计特征"""
        try:
            if len(pitch_vector) == 0:
                return {"mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0}
                
            return {
                "mean": float(np.mean(pitch_vector)),
                "std": float(np.std(pitch_vector)),
                "max": float(np.max(pitch_vector)),
                "min": float(np.min(pitch_vector))
            }
        except Exception as e:
            print(f"音高统计计算错误: {str(e)}")
            return {"mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0}
    
    def _calc_energy_stats(self, energy_vector):
        """计算音量统计特征"""
        try:
            if len(energy_vector) == 0:
                return {"mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0}
                
            return {
                "mean": float(np.mean(energy_vector)),
                "std": float(np.std(energy_vector)),
                "max": float(np.max(energy_vector)),
                "min": float(np.min(energy_vector))
            }
        except Exception as e:
            print(f"音量统计计算错误: {str(e)}")
            return {"mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0} 