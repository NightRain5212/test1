import os
import json
import mysql.connector
from config import DATABASE_CONFIG
from typing import Dict, List, Optional, Union,Any,Tuple # 导入类型提示
from contextlib import contextmanager  # 用于上下文管理器

class DatabaseManager:
    def __init__(self):
        """初始化数据库连接"""
        try:
            self.connection = mysql.connector.connect(**DATABASE_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            self._init_tables()
            print("数据库连接成功")
        except Exception as e:
            print(f"数据库连接失败: {str(e)}")
            raise

    def _init_tables(self):
        """初始化数据库表"""
        try:
            # 创建分析结果表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    video_path VARCHAR(255) NOT NULL,
                    video_analysis JSON,
                    voice_analysis JSON,
                    text_analysis JSON,
                    analysis_result JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建用户表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            # 创建简历表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    file_path VARCHAR(255) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建面试记录表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS interview_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    resume_id INT NOT NULL,
                    video_path VARCHAR(255),
                    audio_path VARCHAR(255),
                    report_path VARCHAR(255),
                    total_score DECIMAL(5,2),
                    rating ENUM('优秀', '良好', '中等', '待提高') NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (resume_id) REFERENCES resumes(id)
                )
            """)

            # 创建面试问题表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS interview_questions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    interview_id INT NOT NULL,
                    question TEXT NOT NULL,
                    answer_audio_path VARCHAR(255),
                    answer_text TEXT,
                    score DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (interview_id) REFERENCES interview_records(id)
                )
            """)

            # 创建社区帖子表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    post_type ENUM('面试题', '实时面试', '经验分享', '资源分享') NOT NULL,
                    tags VARCHAR(255),
                    views INT DEFAULT 0,
                    likes INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建帖子评论表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_comments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    post_id INT NOT NULL,
                    user_id INT NOT NULL,
                    content TEXT NOT NULL,
                    likes INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES community_posts(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建资源链接表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS resource_links (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    url VARCHAR(512) NOT NULL,
                    description TEXT,
                    category VARCHAR(50) NOT NULL,
                    tags VARCHAR(255),
                    clicks INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()

            print("数据库表初始化完成")

        except Exception as e:
            print(f"数据库表初始化失败: {str(e)}")
            raise

    async def save_analysis_result(self, result: Dict[str, Any]) -> int:
        """保存分析结果到数据库"""
        try:
            query = """
                INSERT INTO analysis_results 
                (video_path, video_analysis, voice_analysis, text_analysis, analysis_result)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                result.get("video_path", ""),
                json.dumps(result.get("video_analysis", {})),
                json.dumps(result.get("voice_analysis", {})),
                json.dumps(result.get("text_analysis", {})),
                json.dumps(result.get("analysis_result", {}))
            )

            self.cursor.execute(query, values)
            self.connection.commit()

            return self.cursor.lastrowid

        except Exception as e:
            print(f"保存分析结果失败: {str(e)}")
            self.connection.rollback()
            raise

    async def get_analysis_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        """获取分析结果"""
        try:
            query = "SELECT * FROM analysis_results WHERE id = %s"
            self.cursor.execute(query, (result_id,))
            result = self.cursor.fetchone()

            if result:
                # 将JSON字符串转换回字典
                result["video_analysis"] = json.loads(result["video_analysis"])
                result["voice_analysis"] = json.loads(result["voice_analysis"])
                result["text_analysis"] = json.loads(result["text_analysis"])
                result["analysis_result"] = json.loads(result["analysis_result"])

            return result

        except Exception as e:
            print(f"获取分析结果失败: {str(e)}")
            raise

    def __del__(self):
        """安全关闭数据库连接和游标"""
        try:
            # 关闭游标
            if hasattr(self, 'cursor') and self.cursor is not None:
                try:
                    self.cursor.close()
                except Exception as e:
                    print(f"关闭游标失败: {str(e)}")
                finally:
                    self.cursor = None  # 确保引用被清除

            # 关闭连接
            if hasattr(self, 'conn') and self.connection is not None:
                try:
                    if self.connection.is_connected():  # mysql-connector特有检查
                        self.connection.close()
                except Exception as e:
                    print(f"关闭连接失败: {str(e)}")
                finally:
                    self.connection = None  # 确保引用被清除
        except Exception as e:
            print(f"关闭数据库资源时发生意外错误: {str(e)}")

    def commit(self):
        """提交当前事务"""
        print("提交当前事务-------------------------------------------")
        try:
            self.connection.commit()  # mysql-connector-python 的提交方式
        except mysql.connector.Error as e:  # 异常类不同
            print(f"  提交事务时发生错误: {e}")
            self.connection.rollback()  # 回滚事务
            raise

    def rollback(self):
        """回滚当前事务"""
        self.connection.rollback()

    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

    def _validate_identifier(self, name: str) -> str:
        """验证SQL标识符（表名、列名）防止注入"""
        #暂时不启用
        return name

    def _build_where_clause(self, conditions: Dict[str, Any]) -> Tuple[str, Tuple]:
        """安全构建WHERE子句"""
        where_parts = []
        params = []
        for col, val in conditions.items():
            self._validate_identifier(col)
            where_parts.append(f"{col} = %s")
            params.append(val)
        return " AND ".join(where_parts), tuple(params)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """执行查询操作（安全参数化）"""
        try:
            with self.connection.cursor(dictionary=True ) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            raise

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """执行更新操作（安全参数化）"""
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                affected_rows = cursor.execute(query, params or ())
                self.connection.commit()
                return affected_rows
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"Error executing update: {e}")
            raise

    def insert(self, table: str, data: Dict) -> int:
        """安全插入数据"""
        print("执行插入操作:","插入",data,"到",table,"-------------------------------")
        self._validate_identifier(table)
        columns = ", ".join([self._validate_identifier(col) for col in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute_update(query, tuple(data.values()))

    def select(self, table: str, columns: List[str] = ["*"],
               conditions: Optional[Dict[str, Any]] = None) -> List[Dict]:
        print("执行查询操作:","从",table,"查询",columns,"条件",conditions,"-------------------------------")
        """安全查询数据"""
        self._validate_identifier(table)
        validated_columns = [self._validate_identifier(col) if col != "*" else "*"
                             for col in columns]
        columns_str = ", ".join(validated_columns)

        query = f"SELECT {columns_str} FROM {table}"
        params = ()

        if conditions:
            where_clause, params = self._build_where_clause(conditions)
            query += f" WHERE {where_clause}"

        return self.execute_query(query, params)

    def update(self, table: str, data: Dict,
               conditions: Optional[Dict[str, Any]] = None) -> int:
        """安全更新数据"""
        print("执行更新操作:","更新",data,"到",table,"条件",conditions,"-------------------------------")
        self._validate_identifier(table)
        set_parts = []
        set_params = []
        for col, val in data.items():
            self._validate_identifier(col)
            set_parts.append(f"{col} = %s")
            set_params.append(val)

        query = f"UPDATE {table} SET {', '.join(set_parts)}"
        params = tuple(set_params)

        if conditions:
            where_clause, where_params = self._build_where_clause(conditions)
            query += f" WHERE {where_clause}"
            params += where_params

        return self.execute_update(query, params)

    def delete(self, table: str, conditions: Dict[str, Any]) -> int:
        """安全删除数据"""
        print("执行删除操作:","删除",table,"条件",conditions,"-------------------------------")
        self._validate_identifier(table)
        where_clause, params = self._build_where_clause(conditions)
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_update(query, params)

    # 面试相关的方法
    async def create_resume(self, user_id: int, file_path: str, file_type: str, content: str = None) -> int:
        """创建简历记录"""
        try:
            query = """
                INSERT INTO resumes (user_id, file_path, file_type, content)
                VALUES (%s, %s, %s, %s)
            """
            values = (user_id, file_path, file_type, content)
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"创建简历记录失败: {str(e)}")
            self.conn.rollback()
            raise

    async def create_interview_record(self, user_id: int, resume_id: int) -> int:
        """创建面试记录"""
        try:
            query = """
                INSERT INTO interview_records (user_id, resume_id, rating)
                VALUES (%s, %s, '待提高')
            """
            values = (user_id, resume_id)
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"创建面试记录失败: {str(e)}")
            self.conn.rollback()
            raise

    async def add_interview_question(self, interview_id: int, question: str) -> int:
        """添加面试问题"""
        try:
            query = """
                INSERT INTO interview_questions (interview_id, question)
                VALUES (%s, %s)
            """
            values = (interview_id, question)
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"添加面试问题失败: {str(e)}")
            self.conn.rollback()
            raise

    async def update_question_answer(self, question_id: int, answer_audio_path: str, answer_text: str, score: float) -> None:
        """更新问题的答案"""
        try:
            query = """
                UPDATE interview_questions
                SET answer_audio_path = %s, answer_text = %s, score = %s
                WHERE id = %s
            """
            values = (answer_audio_path, answer_text, score, question_id)
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"更新问题答案失败: {str(e)}")
            self.conn.rollback()
            raise

    async def complete_interview(self, interview_id: int, video_path: str, audio_path: str, 
                               report_path: str, total_score: float, rating: str) -> None:
        """完成面试记录"""
        try:
            query = """
                UPDATE interview_records
                SET video_path = %s, audio_path = %s, report_path = %s, 
                    total_score = %s, rating = %s, is_completed = TRUE
                WHERE id = %s
            """
            values = (video_path, audio_path, report_path, total_score, rating, interview_id)
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"完成面试记录失败: {str(e)}")
            self.conn.rollback()
            raise

    async def get_interview_history(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """获取用户的面试历史记录"""
        try:
            query = """
                SELECT ir.*, r.file_path as resume_path, r.file_type as resume_type
                FROM interview_records ir
                JOIN resumes r ON ir.resume_id = r.id
                WHERE ir.user_id = %s AND ir.is_completed = TRUE
                ORDER BY ir.created_at DESC
                LIMIT %s OFFSET %s
            """
            self.cursor.execute(query, (user_id, limit, offset))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取面试历史记录失败: {str(e)}")
            raise

    async def get_interview_questions(self, interview_id: int) -> List[Dict[str, Any]]:
        """获取面试的所有问题"""
        try:
            query = """
                SELECT *
                FROM interview_questions
                WHERE interview_id = %s
                ORDER BY created_at ASC
            """
            self.cursor.execute(query, (interview_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取面试问题失败: {str(e)}")
            raise

    async def get_interview_details(self, interview_id: int) -> Dict[str, Any]:
        """获取面试详细信息"""
        try:
            query = """
                SELECT ir.*, r.file_path as resume_path, r.file_type as resume_type,
                       r.content as resume_content
                FROM interview_records ir
                JOIN resumes r ON ir.resume_id = r.id
                WHERE ir.id = %s
            """
            self.cursor.execute(query, (interview_id,))
            interview = self.cursor.fetchone()
            
            if interview:
                # 获取该面试的所有问题
                questions = await self.get_interview_questions(interview_id)
                interview['questions'] = questions
                
            return interview
        except Exception as e:
            print(f"获取面试详细信息失败: {str(e)}")
            raise

# 创建单例实例
db_manager = DatabaseManager()