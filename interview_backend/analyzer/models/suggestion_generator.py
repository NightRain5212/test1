import asyncio
from utils.spark_client import SparkClient

class SuggestionGenerator:
    def __init__(self):
        """初始化建议生成器"""
        self.spark_client = SparkClient()

    def generate_suggestions(self, score_result):
        """生成面试建议"""
        try:
            # 准备分析数据
            analysis_data = {
                # 视频数据
                "eyebrow_raise": score_result["details"]["video_data"]["eyebrow_raise"],
                "posture_stability": score_result["details"]["video_data"]["posture_stability"],
                "hand_movement": score_result["details"]["video_data"]["hand_movement"],
                
                # 语音数据
                "speech_rate": score_result["details"]["voice_data"]["speech_rate"],
                "pitch_variation": score_result["details"]["voice_data"]["pitch_variation"],
                "energy_variation": score_result["details"]["voice_data"]["energy_variation"],
                "energy_mean": score_result["details"]["voice_data"].get("energy_mean", 0.0),
                
                # 文本数据
                "keyword_count": score_result["details"]["text_data"]["keyword_count"],
                "content_coherence": score_result["details"]["text_data"]["content_coherence"],
                "resume_similarity": score_result["details"]["text_data"]["resume_similarity"]
            }
            
            # 调用讯飞星火API进行分析
            loop = asyncio.get_event_loop()
            analysis_result = loop.run_until_complete(
                self.spark_client.get_analysis(analysis_data)
            )
            
            if not analysis_result:
                raise Exception("无法获取分析结果")
                
            return analysis_result
            
        except Exception as e:
            print(f"生成建议时出错: {str(e)}")
            return {
                "non_verbal_analysis": "无法分析非语言表现",
                "voice_analysis": "无法分析语音表现",
                "content_analysis": "无法分析内容表现",
                "improvement_suggestions": "暂时无法生成建议",
                "overall_evaluation": "系统暂时无法提供评价",
                "raw_response": str(e)
            } 