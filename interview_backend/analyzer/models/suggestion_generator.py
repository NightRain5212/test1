import json
import asyncio
from spark_client import SparkClient

class SuggestionGenerator:
    def __init__(self):
        """初始化建议生成器"""
        self.spark_client = SparkClient()
        
    def generate_suggestions(self, video_result=None, voice_result=None, text_result=None):
        """
        生成改进建议
        :param video_result: 视频分析结果
        :param voice_result: 语音分析结果
        :param text_result: 文本分析结果
        :return: 建议列表
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(video_result, voice_result, text_result)
            
            # 使用星火大模型生成建议
            result = asyncio.run(self.spark_client.get_analysis(
                video_data=video_result,
                voice_data=voice_result,
                text_data=text_result
            ))
            
            if result["status"] == "success":
                return result["message"]
            else:
                return "无法生成建议，请稍后重试"
                
        except Exception as e:
            print(f"生成建议时出错: {str(e)}")
            return "生成建议时出错，请稍后重试"
            
    def _build_prompt(self, video_result=None, voice_result=None, text_result=None):
        """构建提示词"""
        prompt = "请根据以下分析结果，给出具体的改进建议：\n\n"
        
        if video_result:
            prompt += f"视频表现：\n{json.dumps(video_result, ensure_ascii=False, indent=2)}\n\n"
        if voice_result:
            prompt += f"语音表现：\n{json.dumps(voice_result, ensure_ascii=False, indent=2)}\n\n"
        if text_result:
            prompt += f"内容表现：\n{json.dumps(text_result, ensure_ascii=False, indent=2)}\n\n"
            
        prompt += "请从以下几个方面给出具体的改进建议：\n"
        prompt += "1. 肢体语言和表情管理\n"
        prompt += "2. 语音语调和语速控制\n"
        prompt += "3. 回答内容的专业性和逻辑性\n"
        prompt += "4. 整体表现的综合评价\n"
        
        return prompt 