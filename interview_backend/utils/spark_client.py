import websockets
import json
import hmac
import base64
import datetime
import hashlib
import asyncio
from urllib.parse import urlparse, urlencode
from config import SPARK_CONFIG

class SparkClient:
    def __init__(self):
        self.app_id = SPARK_CONFIG["app_id"]
        self.api_key = SPARK_CONFIG["api_key"]
        self.api_secret = SPARK_CONFIG["api_secret"]
        self.spark_url = SPARK_CONFIG["spark_url"]
        self.domain = SPARK_CONFIG["domain"]

    def _create_url(self):
        """生成请求URL"""
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # 解析URL
        parsed_url = urlparse(self.spark_url)
        
        # 准备签名原文
        signature_origin = f"host: {parsed_url.netloc}\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET {parsed_url.path} HTTP/1.1"

        # 使用hmac-sha256进行签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", '
        authorization_origin += f'headers="host date request-line", signature="{signature_sha_base64}"'
        
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()

        # 组装最终的URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": parsed_url.netloc
        }
        
        return self.spark_url + "?" + urlencode(params)

    def _prepare_message(self, text):
        """准备请求消息体"""
        return {
            "header": {
                "app_id": self.app_id,
                "uid": "interview_assistant"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": 0.5,
                    "max_tokens": 1024
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": text}
                    ]
                }
            }
        }

    async def get_analysis(self, interview_data):
        """获取面试分析结果"""
        prompt = self._generate_analysis_prompt(interview_data)
        
        try:
            url = self._create_url()
            message = self._prepare_message(prompt)
            
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps(message))
                
                response_text = ""
                async for response in websocket:
                    data = json.loads(response)
                    code = data["header"]["code"]
                    
                    if code != 0:
                        print(f"请求错误，错误码：{code}")
                        return None
                        
                    response_text += data["payload"]["choices"]["text"][0]["content"]
                    
                    if data["header"]["status"] == 2:
                        break
                
                return self._parse_analysis_result(response_text)
                
        except Exception as e:
            print(f"调用讯飞星火API出错: {str(e)}")
            return None

    def _generate_analysis_prompt(self, interview_data):
        """生成分析提示词"""
        prompt = """
        请作为专业的面试评估专家，根据以下面试数据进行分析并给出详细的评估和建议：

        视频分析数据：
        - 眉毛动作指数：{eyebrow_raise:.2f}
        - 姿态稳定性：{posture_stability:.2f}
        - 手部动作指数：{hand_movement:.2f}

        语音分析数据：
        - 语速：{speech_rate:.2f}
        - 音调变化：{pitch_variation:.2f}
        - 音量变化：{energy_variation:.2f}
        - 平均音量：{energy_mean:.2f}

        文本分析数据：
        - 关键词匹配度：{keyword_count}
        - 内容连贯性：{content_coherence:.2f}
        - 与简历相关性：{resume_similarity:.2f}

        请从以下几个方面进行分析：
        1. 非语言表现（面部表情、姿态、手势等）
        2. 语音表现（语速、语调、音量等）
        3. 内容表现（专业性、逻辑性、相关性）
        4. 具体改进建议
        5. 总体评价

        请给出详细的分析和具体的改进建议。
        """.format(**interview_data)
        
        return prompt

    def _parse_analysis_result(self, response_text):
        """解析并格式化分析结果"""
        try:
            # 将文本结果解析为结构化数据
            sections = response_text.split("\n\n")
            
            result = {
                "non_verbal_analysis": "",
                "voice_analysis": "",
                "content_analysis": "",
                "improvement_suggestions": "",
                "overall_evaluation": "",
                "raw_response": response_text
            }
            
            for section in sections:
                if "非语言表现" in section:
                    result["non_verbal_analysis"] = section
                elif "语音表现" in section:
                    result["voice_analysis"] = section
                elif "内容表现" in section:
                    result["content_analysis"] = section
                elif "改进建议" in section:
                    result["improvement_suggestions"] = section
                elif "总体评价" in section:
                    result["overall_evaluation"] = section
                    
            return result
            
        except Exception as e:
            print(f"解析分析结果时出错: {str(e)}")
            return {
                "raw_response": response_text
            } 