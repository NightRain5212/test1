import json
from logging import raiseExceptions
from typing import List, Dict, Any
#from ...spark_client import SparkClient
#from ..spark_client import SparkClient
from fastapi import HTTPException
class QuestionGenerator:
    def __init__(self,spark_client):
        self.spark_client = spark_client

    #整理成格式化的内部信息
    async def organize_content(self, resume_content, job):
        try:
            prompt=f"""
从以下文本中提取关键文字信息:{resume_content}。整理为json格式的响应数据。json需包含以下字段:
"姓名""手机号""邮箱""性别""年龄""意向岗位""学历信息""专业""实习经历""学术成就""技能""自我评价",其中“技能"是指兴趣爱好/特长,"学术成就"是指
科研成果/竞赛获奖/做过或者参与的项目,如果无法找到"学历信息""性别""年龄""姓名""意向岗位""专业""技能"这几个字段，就只返回空的json数据。
            """
            prompt1=prompt#推测这里需要自动转换
            response = self.spark_client.chat(prompt1,512)#如果max_tokens过小可能返回空结果
            if not response:  # 检查空数据
                raise HTTPException(
                    status_code=400,
                    detail="无法从简历中提取有效信息"
                )
            return response
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=422,
                detail="简历内容格式解析失败"
            )

        except Exception as e:
            print(f"简历处理发生错误: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"简历处理发生错误: {str(e)}"
            )
    async def generate_questions(self, resume_content: str) -> List[str]:
        """根据简历内容和职位类型生成面试问题"""
        try:
            # 构建提示词
            prompt = f"""
            假设你是一名面试官，要面试一名大学生，现在你需要根据下面的简历信息来生成几个问题:{resume_content}
            要求:
            1.请受试者进行剪短的自我介绍
            2.根据简历的"意向岗位"和”专业"相关的内容，提出几个理论层面的面试问题，以考察基本功底。
            3.根据简历的"实习经历、过往成就、做过的项目“相关内容生成至少3个问题。
            4.根据兴趣爱好或潜能等相关信息，针对性提出几个情景式的问题，例如遇到某某某情况应当如何处理，你对xxx有什么看法等。
            5.根据相关内容，提出一些与伦理抉择相关的问题，例如:如果有更好的薪资，是否会选择转行、如果对公司有一些建议，应当怎么做
            返回结果为列表,格式为： ["问题1","问题2","问题3",“..."]
             """
            prompt1=prompt
            # 调用讯飞星火API生成问题
            response = self.spark_client.chat(prompt1,1024)
            if not response:  # 检查空数据
                print("无法从简历中提取有效信息")
                raise HTTPException(
                    status_code=400,
                    detail="无法从简历中提取有效信息"
                )
            print("response:",response)
            return response

        except HTTPException as e:
            print(str(e))
            raise
        except Exception as e:
            print(f"生成面试问题失败: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail=f"分析简历出错:{str(e)}"
            )

    async def evaluate_answer(self, question: str, answer: str, job_type: str) -> Dict[str, Any]:
        """评估面试答案"""
        try:
            prompt = f"""
            作为面试官，请评估以下面试问答的表现。职位是：{job_type}

            问题：{question}
            答案：{answer}

            请从以下几个方面进行评估：
            1. 专业性（对专业知识的理解和运用）
            2. 完整性（是否完整回答了问题）
            3. 逻辑性（思路是否清晰）
            4. 实践性（是否结合实际经验）

            请以JSON格式返回评估结果，格式为：
            {{
                "score": 85,  # 总分（0-100）
                "feedback": "详细的评价反馈",
                "strengths": ["优点1", "优点2"],
                "improvements": ["建议1", "建议2"]
            }}
            """

            # 调用讯飞星火API评估答案
            response = await self.spark_client.chat(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # 返回默认评估结果
                return {
                    "score": 60,
                    "feedback": "无法解析评估结果",
                    "strengths": ["回答了问题"],
                    "improvements": ["建议提供更多细节"]
                }

        except Exception as e:
            print(f"评估面试答案失败: {str(e)}")
            return {
                "score": 60,
                "feedback": "评估过程发生错误",
                "strengths": ["已完成回答"],
                "improvements": ["建议重新回答"]
            }

    def calculate_rating(self, total_score: float) -> str:
        """根据总分计算评级"""
        if total_score >= 90:
            return "优秀"
        elif total_score >= 80:
            return "良好"
        elif total_score >= 60:
            return "中等"
        else:
            return "待提高" 