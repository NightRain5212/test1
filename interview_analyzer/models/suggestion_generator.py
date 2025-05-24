from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from datetime import datetime

class SuggestionGenerator:
    def __init__(self, model_name="internlm/internlm2-chat-7b"):
        """
        初始化建议生成器
        model_name: 使用的大模型名称
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        
    def generate_suggestions(self, analysis_result):
        """根据分析结果生成建议"""
        prompt = self._build_prompt(analysis_result)
        
        # 生成回答
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            inputs.input_ids,
            max_new_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return self._parse_response(response)
        
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