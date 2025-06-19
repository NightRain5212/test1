import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import mysql.connector
from config import DATABASE_CONFIG

class DatabaseManager:
    def __init__(self):
        """初始化数据库连接"""
        try:
            self.conn = mysql.connector.connect(**DATABASE_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
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
            
            self.conn.commit()
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
            self.conn.commit()
            
            return self.cursor.lastrowid
            
        except Exception as e:
            print(f"保存分析结果失败: {str(e)}")
            self.conn.rollback()
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
        """关闭数据库连接"""
        try:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print(f"关闭数据库连接失败: {str(e)}")

# 创建单例实例
db_manager = DatabaseManager()