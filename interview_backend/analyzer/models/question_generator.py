import json
from logging import raiseExceptions
from typing import List, Dict, Any
#from ...spark_client import SparkClient
#from ..spark_client import SparkClient
from interview_backend.spark_client import SparkClient
from fastapi import HTTPException
class QuestionGenerator:
    def __init__(self):
        self.spark_client = SparkClient()

    #整理成格式化的内部信息
    async def organize_content(self, resume_content: str, job: str):
        try:
            prompt=f"""
从以下文本中提取关键文字信息:{resume_content}    整理为json格式的响应数据。json需包含以下字段:
"姓名""手机号""邮箱""性别""年龄""意向岗位""学历信息""专业""实习经历""学术成就""技能""自我评价",其中“技能"是指兴趣爱好/特长,"学术成就"是指
科研成果/竞赛获奖/做过或者参与的项目,如果无法找到"学历信息""性别""年龄""姓名""意向岗位""专业""技能"这几个字段，就只返回空的json数据。
            """
            response = await self.spark_client.chat(prompt)
            # 尝试解析JSON响应
            resume_data = json.loads(response)
            if not resume_data:  # 检查空数据
                raise HTTPException(
                    status_code=400,
                    detail="无法从简历中提取有效信息"
                )
            return resume_data
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=422,
                detail="简历内容格式解析失败"
            )

        except Exception as e:
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
            
            问题应该大体涵盖：
            1. 专业技能考察
            2. 项目经验深度
            3. 解决问题能力
            4. 学习能力和发展潜力
            5. 团队协作能力

            请生成的问题要专业、有深度，能够考察候选人的实际能力。
            额外提示:
            1.请受试者进行剪短的自我介绍
            2.根据简历的"意向岗位"和”专业"相关的内容，提出几个理论层面的面试问题，以考察基本功底。
            3.根据简历的"实习经历、过往成就、做过的项目“相关内容生成至少3个问题。
            4.根据兴趣爱好或潜能等相关信息，针对性提出几个情景式的问题，例如遇到某某某情况应当如何处理，你对xxx有什么看法等。
            5.根据相关内容，提出一些与伦理抉择相关的问题，例如:如果有更好的薪资，是否会选择转行、如果对公司有一些建议，应当怎么做
            请以JSON格式返回问题列表，格式为：
            {{"questions": ["问题1", "问题2", "问题3", "问题4", "问题5"]}}
            """

            # 调用讯飞星火API生成问题
            response = await self.spark_client.chat(prompt)
            
            try:
                # 尝试解析JSON响应
                questions_data = json.loads(response)
                return questions_data.get("questions", [])
            except json.JSONDecodeError:
                # 如果返回的不是JSON格式，尝试从文本中提取问题
                questions = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and line[0].isdigit() and '.' in line:
                        question = line.split('.', 1)[1].strip()
                        questions.append(question)
                return questions

        except Exception as e:
            print(f"生成面试问题失败: {str(e)}")
            # 返回一些默认问题
            return [
                f"请介绍一下你在这个专业方面的经验和技能。",
                "能否分享一个你最有挑战性的项目经历？",
                "你是如何处理工作中的技术难题的？",
                "你最近在学习什么新技术？为什么选择学习它？",
                "你是如何与团队成员协作完成项目的？"
            ]

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