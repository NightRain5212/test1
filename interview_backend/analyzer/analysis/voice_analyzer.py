import whisper
import numpy as np
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import ShortTermFeatures as sF
import os
from pathlib import Path
import subprocess
from datetime import datetime
from config import AUDIO_DIR
import asyncio

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
            
    async def analyze(self, video_path):
        """分析视频中的语音"""
        try:
            # 提取音频
            audio_path = await self._extract_audio(video_path)
            
            # 语音识别
            text = await self._transcribe_audio(audio_path)
            
            # 分析语音特征
            features = await self._analyze_features(audio_path)
            
            # 计算总分
            total = (
                features["speech_rate"] * 0.2 +
                features["pitch_variation"] * 0.3 +
                features["energy_variation"] * 0.2 +
                features["energy_mean"] * 0.3
            )
            
            return {
                "total": float(total),
                "details": features,
                "text": text
            }
            
        except Exception as e:
            print(f"语音分析错误: {str(e)}")
            return {
                "total": 0.0,
                "details": {
                    "speech_rate": 0.0,
                    "pitch_variation": 0.0,
                    "energy_variation": 0.0,
                    "energy_mean": 0.0
                },
                "text": ""
            }
    
    async def _extract_audio(self, video_path):
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
            process = await asyncio.create_subprocess_exec(
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # 不处理视频
                '-acodec', 'pcm_s16le',  # 音频编码
                '-ar', '44100',  # 采样率
                '-ac', '2',  # 声道数
                '-y',  # 覆盖已存在的文件
                str(audio_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise ValueError(f"音频提取失败: {stderr.decode()}")
            
            return str(audio_path)
            
        except Exception as e:
            print(f"音频提取错误: {str(e)}")
            raise
    
    async def _transcribe_audio(self, audio_path):
        """转录音频为文本"""
        try:
            # 使用 whisper 进行语音识别
            result = await asyncio.to_thread(
                self.model.transcribe,
                audio_path,
                language="zh"
            )
            
            return result["text"]
            
        except Exception as e:
            print(f"语音识别错误: {str(e)}")
            return ""
    
    async def _analyze_features(self, audio_path):
        """分析语音特征"""
        try:
            # 使用 ffmpeg 提取音频特征
            process = await asyncio.create_subprocess_exec(
                'ffmpeg',
                '-i', str(audio_path),
                '-af', 'astats=metadata=1:reset=1',
                '-f', 'null',
                '-',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise ValueError(f"音频特征提取失败: {stderr.decode()}")
            
            # 解析音频特征
            features = self._parse_audio_features(stderr.decode())
            
            return features
            
        except Exception as e:
            print(f"音频特征分析错误: {str(e)}")
            return {
                "speech_rate": 0.0,
                "pitch_variation": 0.0,
                "energy_variation": 0.0,
                "energy_mean": 0.0
            }
    
    def _parse_audio_features(self, ffmpeg_output):
        """解析 ffmpeg 输出的音频特征"""
        try:
            # 提取音频特征
            lines = ffmpeg_output.split('\n')
            features = {}
            
            for line in lines:
                if "RMS level dB" in line:
                    features["energy_mean"] = float(line.split(':')[1].strip())
                elif "Peak level dB" in line:
                    features["energy_variation"] = float(line.split(':')[1].strip())
                elif "Flatness" in line:
                    features["pitch_variation"] = float(line.split(':')[1].strip())
                elif "Duration" in line:
                    duration = float(line.split(':')[1].strip().split(' ')[0])
                    features["speech_rate"] = 1.0 / duration if duration > 0 else 0.0
            
            # 归一化特征值
            for key in features:
                if key == "energy_mean":
                    features[key] = (features[key] + 60) / 60  # 归一化到 0-1
                elif key == "energy_variation":
                    features[key] = (features[key] + 60) / 60  # 归一化到 0-1
                elif key == "pitch_variation":
                    features[key] = min(features[key], 1.0)  # 限制在 0-1
                elif key == "speech_rate":
                    features[key] = min(features[key], 1.0)  # 限制在 0-1
            
            return features
            
        except Exception as e:
            print(f"音频特征解析错误: {str(e)}")
            return {
                "speech_rate": 0.0,
                "pitch_variation": 0.0,
                "energy_variation": 0.0,
                "energy_mean": 0.0
            }
    
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