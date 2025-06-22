import json
from typing import List, Dict, Any
from ...spark_client import SparkClient

class QuestionGenerator:
    def __init__(self):
        self.spark_client = SparkClient()

    async def generate_questions(self, resume_content: str, job_type: str) -> List[str]:
        """根据简历内容和职位类型生成面试问题"""
        try:
            # 构建提示词
            prompt = f"""
            作为面试官，请根据以下简历内容，为{job_type}职位生成5个专业的面试问题。
            问题应该涵盖：
            1. 专业技能考察
            2. 项目经验深度
            3. 解决问题能力
            4. 学习能力和发展潜力
            5. 团队协作能力

            简历内容：
            {resume_content}

            请生成的问题要专业、有深度，能够考察候选人的实际能力。
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
                return questions[:5]  # 只返回前5个问题

        except Exception as e:
            print(f"生成面试问题失败: {str(e)}")
            # 返回一些默认问题
            return [
                f"请介绍一下你在{job_type}方面的经验和技能。",
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