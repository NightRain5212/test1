import requests
from datetime import datetime
from dotenv import load_dotenv
API_TOKEN = "your_huggingface_api_token_here"

class SuggestionGenerator:
    def __init__(self, model_name="internlm/internlm2-chat-7b", api_token=API_TOKEN):
        """
        初始化建议生成器
        model_name: 使用的大模型名称
        api_token: HuggingFace API token
        """
        self.model_name = model_name
        self.api_token = api_token
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}

    def generate_suggestions(self, analysis_result):
        """根据分析结果生成建议"""
        prompt = self._build_prompt(analysis_result)
        
        # 通过API生成回答
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt, "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                }}
            )
            response.raise_for_status()
            result = response.json()
            
            # API返回格式可能因模型而异，这里假设返回的是列表中的第一个结果
            generated_text = result[0]["generated_text"] if isinstance(result, list) else result["generated_text"]
            
            return self._parse_response(generated_text)
            
        except Exception as e:
            return {
                "raw_response": f"生成建议时发生错误: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error": True
            }
        
    def _build_prompt(self, data):
        """构建提示词"""
        scores = data["scores"]
        details = data["details"]
        
        prompt = f"""作为一位资深面试官，请根据以下面试分析数据给出详细的评价和改进建议：

1. 总体表现：
- 总分：{scores['total']:.2f}/100
- 视频表现：{scores['video']:.2f}/100
- 语音表现：{scores['voice']:.2f}/100
- 文本表现：{scores['text']:.2f}/100

2. 具体指标：
视频分析：
- 眉毛动作频率（紧张指标）：{details['video_data']['eyebrow_raise']:.3f}
- 坐姿稳定性：{details['video_data']['posture_stability']:.3f}
- 手部动作频率：{details['video_data']['hand_movement']:.3f}

语音分析：
- 语速：{details['voice_data']['speech_rate']:.2f} 字/秒
- 音高变化：{details['voice_data']['pitch_variation']:.3f}
- 音量变化：{details['voice_data']['energy_variation']:.3f}

文本分析：
- 关键词匹配数：{details['text_data']['keyword_count']}
- 内容连贯性：{details['text_data']['content_coherence']:.3f}
- 与简历相关度：{details['text_data']['resume_similarity']:.3f}

请提供：
1. 总体评价
2. 各维度的具体分析（视频表现、语音表现、内容表现）
3. 针对性的改进建议（至少3条）
4. 优势亮点（至少2点）

请用中文回答，并注重实用性和可操作性。"""

        return prompt
        
    def _parse_response(self, response):
        """解析模型回答"""
        # 移除可能的提示词部分
        if "请提供：" in response:
            response = response.split("请提供：")[-1]
            
        return {
            "raw_response": response,
            "timestamp": datetime.now().isoformat()
        }

    def generate_suggestions(self, score_result):
        """根据得分生成建议"""
        # 这里是示例实现，实际应该包含更复杂的建议生成逻辑
        scores = score_result["scores"]
        suggestions = []
        
        if scores["video"] < 0.6:
            suggestions.append("建议改善面部表情和姿态，保持自然和专业。")
        if scores["voice"] < 0.6:
            suggestions.append("建议调整语速和语调，使表达更加清晰有力。")
        if scores["text"] < 0.6:
            suggestions.append("建议提高回答的相关性和完整性，更好地结合自身经验。")
            
        if not suggestions:
            suggestions.append("整体表现不错，继续保持！")
            
        return {
            "raw_response": "\n".join(suggestions)
        } 