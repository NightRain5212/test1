import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import ssl
import websocket
from datetime import datetime
from time import mktime
from urllib.parse import urlparse, urlencode
from wsgiref.handlers import format_date_time
from config import SPARK_CONFIG
import os
from typing import List, Dict, Any, Optional

import websockets

class SparkClient:
    def __init__(self):
        """初始化星火大模型客户端"""
        self.appid = SPARK_CONFIG["app_id"]
        self.api_key = SPARK_CONFIG["api_key"]
        self.api_secret = SPARK_CONFIG["api_secret"]
        self.spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # Max环境
        self.domain = "generalv3.5"  # Max版本
        self.response_content = ""  # 用于存储响应内容
        
        # 检查配置是否完整
        self._check_config()
        
    def _check_config(self):
        """检查配置是否完整"""
        if not all([self.appid, self.api_key, self.api_secret]):
            raise ValueError(
                "星火大模型配置不完整，请检查 .env 文件中的以下配置：\n"
                "SPARK_APP_ID=你的应用ID\n"
                "SPARK_API_KEY=你的API密钥\n"
                "SPARK_API_SECRET=你的API密钥"
            )
            
        print(f"使用星火大模型配置：")
        print(f"- AppID: {self.appid}")
        print(f"- API Key: {self.api_key[:8]}...")
        print(f"- API Secret: {self.api_secret[:8]}...")
        print(f"- URL: {self.spark_url}")
        print(f"- Domain: {self.domain}")
        
        # 验证域名
        url_parts = urlparse(self.spark_url)
        if url_parts.netloc != "spark-api.xf-yun.com":
            raise ValueError(f"无效的域名: {url_parts.netloc}，应为 spark-api.xf-yun.com")
        
    def _create_url(self):
        """生成鉴权URL"""
        try:
            # 生成RFC1123格式的时间戳
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))
            
            # 解析URL
            url_parts = urlparse(self.spark_url)
            host = url_parts.netloc
            path = url_parts.path

            print(f"准备签名...")
            print(f"- Host: {host}")
            print(f"- Path: {path}")
            print(f"- Date: {date}")

            # 拼接字符串
            signature_origin = "host: " + host + "\n"
            signature_origin += "date: " + date + "\n"
            signature_origin += "GET " + path + " HTTP/1.1"

            print(f"原始签名字符串:\n{signature_origin}")

            # 进行hmac-sha256进行加密
            signature_sha = hmac.new(
                self.api_secret.encode('utf-8'),
                signature_origin.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()

            signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
            print(f"签名结果: {signature_sha_base64}")

            authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

            # 将请求的鉴权参数组合为字典
            v = {
                "authorization": authorization,
                "date": date,
                "host": host
            }
            
            # 拼接鉴权参数，生成url
            url = self.spark_url + '?' + urlencode(v)
            print(f"生成鉴权URL成功: {url}")
            return url
            
        except Exception as e:
            print(f"生成鉴权URL失败: {str(e)}")
            raise

    def _on_error(self, ws, error):
        """WebSocket错误处理"""
        error_msg = f"WebSocket错误: {str(error)}"
        if "401" in str(error):
            error_msg += "\n可能的原因：\n1. AppID不存在或已失效\n2. API密钥不正确\n3. 签名计算错误"
        elif "11200" in str(error):
            error_msg += "\n错误码11200通常表示AppID不存在或已失效，请检查配置"
        print(error_msg)
        
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭处理"""
        print(f"WebSocket连接关闭: 状态码={close_status_code}, 消息={close_msg}")
        
    def _on_open(self, ws):
        """WebSocket连接建立处理"""
        def run(*args):
            data = json.dumps(self._gen_params(ws.query))
            print(f"发送数据: {data}")
            ws.send(data)
        thread.start_new_thread(run, ())
        
    def _on_message(self, ws, message):
        """WebSocket消息处理"""
        try:
            data = json.loads(message)
            code = data['header']['code']
            if code != 0:
                error_msg = f"请求错误: 错误码={code}"
                if code == 11200:
                    error_msg += "\n错误码11200表示AppID不存在或已失效，请检查配置"
                print(error_msg)
                print(f"完整响应: {data}")
                ws.close()
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                self.response_content += content
                if status == 2:
                    print("#### 会话结束 ####")
                    ws.close()
        except Exception as e:
            print(f"处理消息时出错: {str(e)}")
            ws.close()
                
    def _gen_params(self, query):
        """生成请求参数"""
        data = {
            "header": {
                "app_id": self.appid,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": [{"role": "user", "content": query}]
                }
            }
        }
        return data
        
    async def analyze_interview(self, video_path=None, audio_path=None, text=None):
        """分析面试表现"""
        try:
            # 构建提示词
            prompt = self._build_prompt(video_path, audio_path, text)
            
            # 重置响应内容
            self.response_content = ""
            
            # 创建WebSocket连接
            ws_url = self._create_url()
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            ws.query = prompt
            
            # 运行WebSocket连接
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # 返回分析结果
            return {
                "status": "success",
                "message": self.response_content
            }
            
        except Exception as e:
            print(f"分析过程出错: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def _build_prompt(self, video_path=None, audio_path=None, text=None):
        """构建提示词"""
        prompt = "请分析以下面试表现：\n\n"
        
        if video_path:
            prompt += f"视频文件：{video_path}\n"
        if audio_path:
            prompt += f"音频文件：{audio_path}\n"
        if text:
            prompt += f"面试内容：{text}\n"
            
        prompt += "\n请从以下几个方面给出专业的分析和建议：\n"
        prompt += "1. 肢体语言和表情管理\n"
        prompt += "2. 语音语调和语速控制\n"
        prompt += "3. 回答内容的专业性和逻辑性\n"
        prompt += "4. 整体表现的综合评价\n"
        
        return prompt

    async def get_analysis(self, video_data=None, voice_data=None, text_data=None):
        """获取分析结果"""
        try:
            # 构建提示词
            prompt = self._build_prompt(video_data, voice_data, text_data)
            
            # 创建WebSocket连接
            ws_url = self._create_url()
            websocket.enableTrace(False)
            
            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            ws.query = prompt
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            return {"status": "success", "message": "分析完成"}
            
        except Exception as e:
            print(f"分析过程出错: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def _build_prompt(self, video_data=None, voice_data=None, text_data=None):
        """构建提示词"""
        prompt = "请分析以下面试表现：\n\n"
        
        if video_data:
            prompt += f"视频分析结果：\n{json.dumps(video_data, ensure_ascii=False, indent=2)}\n\n"
        if voice_data:
            prompt += f"语音分析结果：\n{json.dumps(voice_data, ensure_ascii=False, indent=2)}\n\n"
        if text_data:
            prompt += f"文本分析结果：\n{json.dumps(text_data, ensure_ascii=False, indent=2)}\n\n"
            
        prompt += "请根据以上数据，给出专业的面试表现评价和改进建议。"
        return prompt

    async def analyze_interview(self, 
                              video_analysis: Dict[str, Any],
                              voice_analysis: Dict[str, Any],
                              text_analysis: Dict[str, Any],
                              job_type: str) -> Dict[str, Any]:
        """分析面试表现并生成建议"""
        # 构建提示词
        prompt = f"""请作为一位专业的面试官，根据以下面试表现数据，生成一份详细的面试分析报告。
面试岗位：{job_type}

视频分析结果：
- 面部表情：{video_analysis.get('facial_emotions', {})}
- 姿态分析：{video_analysis.get('posture', {})}
- 手势分析：{video_analysis.get('gestures', {})}

语音分析结果：
- 语速：{voice_analysis.get('speech_rate', {})}
- 语调：{voice_analysis.get('tone', {})}
- 音量：{voice_analysis.get('volume', {})}

文本分析结果：
- 关键词匹配：{text_analysis.get('keyword_matching', {})}
- 内容连贯性：{text_analysis.get('coherence', {})}
- 回答完整性：{text_analysis.get('completeness', {})}

请生成一份包含以下内容的分析报告：
1. 总体评分（0-100分）
2. 优势分析
3. 需要改进的地方
4. 具体建议
5. 总结评价

请用专业、客观的语气进行分析，并给出具体的改进建议。"""

        try:
            # 调用星火大模型
            print("开始调用星火大模型...")
            response = await self._get_response([{
                "role": "user",
                "content": prompt
            }])
            print("星火大模型响应成功")
            
            # 解析响应
            try:
                analysis_result = json.loads(response)
            except json.JSONDecodeError:
                # 如果响应不是JSON格式，尝试提取关键信息
                analysis_result = {
                    "scores": {
                        "total": self._extract_score(response),
                        "video": video_analysis.get('score', 0),
                        "voice": voice_analysis.get('score', 0),
                        "text": text_analysis.get('score', 0)
                    },
                    "analysis": response,
                    "suggestions": self._extract_suggestions(response)
                }
            
            return analysis_result
            
        except Exception as e:
            print(f"分析过程出错: {str(e)}")
            raise

    def _extract_score(self, text: str) -> float:
        """从文本中提取分数"""
        try:
            # 尝试查找"总分：XX"或"总体评分：XX"这样的模式
            import re
            score_match = re.search(r'[总分|总体评分]：?(\d+)', text)
            if score_match:
                return float(score_match.group(1))
            return 0.0
        except:
            return 0.0

    def _extract_suggestions(self, text: str) -> List[str]:
        """从文本中提取建议"""
        try:
            # 尝试查找"建议"部分
            import re
            suggestions = []
            suggestion_section = re.search(r'建议[：:](.*?)(?=\n\n|$)', text, re.DOTALL)
            if suggestion_section:
                # 按序号或项目符号分割
                items = re.split(r'\d+[.、]|\*|\-', suggestion_section.group(1))
                suggestions = [item.strip() for item in items if item.strip()]
            return suggestions
        except:
            return []

    def _check_config(self):
        """检查配置是否完整"""
        if not all([self.appid, self.api_key, self.api_secret]):
            print("警告：星火大模型配置不完整，将使用本地生成方法")
            self._use_local = True
        else:
            self._use_local = False

    async def chat(self, prompt):
        """调用星火大模型API进行对话"""
        # 如果配置不完整，使用本地生成方法
        if self._use_local:
            return self._local_generate(prompt)
            
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
                        return self._local_generate(prompt)
                        
                    response_text += data["payload"]["choices"]["text"][0]["content"]
                    
                    if data["header"]["status"] == 2:
                        break
                
                return response_text
                
        except Exception as e:
            print(f"调用星火API出错: {str(e)}")
            return self._local_generate(prompt)

    def _local_generate(self, prompt):
        """本地生成回复的方法"""
        try:
            # 基于提示词类型生成不同的回复
            if "面试问题" in prompt or "简历" in prompt:
                return self._generate_interview_questions(prompt)
            elif "分析" in prompt:
                return self._generate_basic_analysis()
            else:
                return "抱歉，我暂时无法处理这个请求。"
        except Exception as e:
            print(f"生成回复时出错: {str(e)}")
            return self._get_default_response()

    def _generate_interview_questions(self, prompt):
        """根据简历和职位生成面试问题"""
        # 提取职位信息
        job_type = "技术岗位"
        if "职位类型" in prompt:
            job_type = prompt.split("职位类型：")[-1].split("\n")[0].strip()

        questions = [
            f"根据您应聘{job_type}的情况，请简单介绍一下您的相关工作经验。",
            f"您认为{job_type}最重要的技能是什么？您是如何掌握这些技能的？",
            "您能描述一下您参与过的最有挑战性的项目吗？",
            "您是如何处理工作中的技术难题的？",
            "您对未来的职业发展有什么规划？"
        ]
        
        # 如果提示词中包含简历内容，生成更有针对性的问题
        if "简历内容：" in prompt:
            resume_text = prompt.split("简历内容：")[-1].split("\n\n")[0].strip()
            if "项目经验" in resume_text or "工作经历" in resume_text:
                questions.append("能具体说说您在简历中提到的项目中担任了什么角色，解决了什么问题吗？")
            if "技能" in resume_text or "专业技术" in resume_text:
                questions.append("您提到了掌握多项技术，能分享一下您是如何持续学习和提升技术能力的吗？")

        # 随机选择3个问题
        import random
        selected_questions = random.sample(questions, min(3, len(questions)))
        return "\n".join(f"{i+1}. {q}" for i, q in enumerate(selected_questions))

    def _generate_basic_analysis(self):
        """生成基础分析报告"""
        return """面试表现分析：

1. 非语言表现：
- 保持了适当的眼神交流
- 姿态自然大方
- 手势使用恰当

2. 语音表现：
- 语速适中
- 语气清晰
- 音量适中

3. 内容表现：
- 回答切题
- 逻辑清晰
- 举例恰当

4. 改进建议：
- 可以准备更多具体的案例
- 建议进一步突出个人优势
- 可以加强专业术语的使用

5. 总体评价：
表现良好，展现了专业素养和沟通能力。"""

    def _get_default_response(self):
        """返回默认回复"""
        return "面试问题生成完成。请开始回答第一个问题。"

    def _prepare_message(self, text):
        """准备请求消息体"""
        return {
            "header": {
                "app_id": self.appid,
                "uid": "user"
            },
            "parameter": {
                "chat": {
                    "domain": "general",
                    "temperature": 0.5,
                    "max_tokens": 2048
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

    async def get_analysis(self, analysis_data):
        """获取面试分析结果"""
        try:
            # 构建分析提示词
            prompt = self._build_analysis_prompt(analysis_data)
            
            # 调用星火API
            response = await self._get_response([{
                "role": "user",
                "content": prompt
            }])
            
            if not response:
                raise Exception("API调用失败")
                
            return response
            
        except Exception as e:
            print(f"获取分析结果时出错: {str(e)}")
            raise
            
    def _build_analysis_prompt(self, data):
        """构建分析提示词"""
        return f"""请根据以下面试表现数据生成详细的分析报告：

视频表现：
- 眉毛动作频率：{data.get('eyebrow_raise', 0):.2f}
- 姿态稳定性：{data.get('posture_stability', 0):.2f}
- 手部动作幅度：{data.get('hand_movement', 0):.2f}

语音表现：
- 语速：{data.get('speech_rate', 0):.2f}
- 音调变化：{data.get('pitch_variation', 0):.2f}
- 音量变化：{data.get('energy_variation', 0):.2f}
- 平均音量：{data.get('energy_mean', 0):.2f}

内容表现：
- 关键词匹配度：{data.get('keyword_count', 0):.2f}
- 内容连贯性：{data.get('content_coherence', 0):.2f}
- 与简历相关性：{data.get('resume_similarity', 0):.2f}

请从以下几个方面进行分析：
1. 非语言表现（面部表情、姿态、手势等）
2. 语音表现（语速、语调、音量等）
3. 内容表现（表达逻辑、关键词使用、与简历的关联等）
4. 改进建议
5. 总体评价

请用专业、客观的语言进行分析，并给出具体的改进建议。"""

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