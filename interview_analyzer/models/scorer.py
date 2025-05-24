import numpy as np
from datetime import datetime

class InterviewScorer:
    def __init__(self, weights=None):
        """
        初始化评分系统
        weights: 各维度的权重配置
        """
        self.weights = weights or {
            "video": {
                "eyebrow_raise": 0.3,
                "posture_stability": 0.4,
                "hand_movement": 0.3
            },
            "voice": {
                "speech_rate": 0.2,
                "pitch_variation": 0.3,
                "energy_variation": 0.2,
                "energy_mean": 0.3
            },
            "text": {
                "keyword_count": 0.3,
                "content_coherence": 0.4,
                "resume_similarity": 0.3
            },
            "dimension": {
                "video": 0.3,
                "voice": 0.3,
                "text": 0.4
            }
        }
        self.history = []
        
    def calculate_score(self, video_data, voice_data, text_data):
        """计算综合评分"""
        # 计算视频维度得分
        video_score = self._calculate_video_score(video_data)
        
        # 计算语音维度得分
        voice_score = self._calculate_voice_score(voice_data)
        
        # 计算文本维度得分
        text_score = self._calculate_text_score(text_data)
        
        # 计算总分
        total_score = (
            self.weights["dimension"]["video"] * video_score +
            self.weights["dimension"]["voice"] * voice_score +
            self.weights["dimension"]["text"] * text_score
        )
        
        # 记录评分历史
        score_record = {
            "timestamp": datetime.now().isoformat(),
            "scores": {
                "video": video_score,
                "voice": voice_score,
                "text": text_score,
                "total": total_score
            },
            "details": {
                "video_data": video_data,
                "voice_data": voice_data,
                "text_data": text_data
            }
        }
        self.history.append(score_record)
        
        return score_record
    
    def _calculate_video_score(self, data):
        """计算视频维度得分"""
        if not data:
            return 0.0
            
        # 归一化处理
        eyebrow_score = 1 - min(data["eyebrow_raise"] * 5, 1)  # 眉毛动作越少越好
        posture_score = data["posture_stability"]  # 已经是0-1的值
        hand_score = 1 - min(data["hand_movement"] * 3, 1)  # 手部动作越少越好
        
        return (
            self.weights["video"]["eyebrow_raise"] * eyebrow_score +
            self.weights["video"]["posture_stability"] * posture_score +
            self.weights["video"]["hand_movement"] * hand_score
        )
    
    def _calculate_voice_score(self, data):
        """计算语音维度得分"""
        if not data:
            return 0.0
            
        # 归一化处理
        speech_rate_score = self._normalize_speech_rate(data["speech_rate"])
        pitch_score = self._normalize_value(data["pitch_variation"], 0.1, 0.3)
        energy_var_score = self._normalize_value(data["energy_variation"], 0.1, 0.3)
        energy_mean_score = self._normalize_value(data["energy_mean"], 0.3, 0.7)
        
        return (
            self.weights["voice"]["speech_rate"] * speech_rate_score +
            self.weights["voice"]["pitch_variation"] * pitch_score +
            self.weights["voice"]["energy_variation"] * energy_var_score +
            self.weights["voice"]["energy_mean"] * energy_mean_score
        )
    
    def _calculate_text_score(self, data):
        """计算文本维度得分"""
        if not data:
            return 0.0
            
        # 归一化处理
        keyword_score = min(data["keyword_count"] / 10, 1.0)  # 假设10个关键词匹配为满分
        coherence_score = data["content_coherence"]  # 已经是0-1的值
        similarity_score = data["resume_similarity"]  # 已经是0-1的值
        
        return (
            self.weights["text"]["keyword_count"] * keyword_score +
            self.weights["text"]["content_coherence"] * coherence_score +
            self.weights["text"]["resume_similarity"] * similarity_score
        )
    
    def _normalize_speech_rate(self, rate):
        """归一化语速分数"""
        # 假设理想语速为3-5字/秒
        if rate < 3:
            return rate / 3
        elif rate > 5:
            return max(0, 1 - (rate - 5) / 3)
        else:
            return 1.0
    
    def _normalize_value(self, value, min_threshold, max_threshold):
        """归一化数值到0-1范围"""
        if value < min_threshold:
            return value / min_threshold
        elif value > max_threshold:
            return max(0, 1 - (value - max_threshold) / max_threshold)
        else:
            return 1.0
            
    def update_weights(self, new_weights):
        """更新评分权重"""
        self.weights.update(new_weights) 