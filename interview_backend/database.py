import pymysql
import dotenv
import os
from typing import Dict, List, Optional, Union
#数据库：username/password/email/created_data(data类型)
class DatabaseManager:
    def __init__(self):
        """初始化数据库连接"""
        dotenv.load_dotenv()
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_NAME = "users"  # 可以改为从环境变量读取
        self.timeout = 20
        
        self.connection = None
        self.connect()

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=self.timeout,
                cursorclass=pymysql.cursors.DictCursor,
                db=self.DB_NAME,
                host=self.DB_HOST,
                password=self.DB_PASSWORD,
                read_timeout=self.timeout,
                port=int(self.DB_PORT),
                user=self.DB_USER,
                write_timeout=self.timeout,
            )
            print("Database connection established")
        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        执行查询操作（SELECT）
        :param query: SQL查询语句
        :param params: 查询参数
        :return: 查询结果列表
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except pymysql.MySQLError as e:
            print(f"Error executing query: {e}")
            raise

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        执行更新操作（INSERT/UPDATE/DELETE）
        :param query: SQL语句
        :param params: 参数
        :return: 受影响的行数
        """
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params or ())
                self.connection.commit()
                return affected_rows
        except pymysql.MySQLError as e:
            self.connection.rollback()
            print(f"Error executing update: {e}")
            raise

    # 以下是具体的CRUD操作方法
    def insert(self, table: str, data: Dict) -> int:
        """
        插入数据
        :param table: 表名
        :param data: 要插入的数据字典 {列名: 值}
        :return: 受影响的行数
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute_update(query, tuple(data.values()))

    def select(self, table: str, columns: List[str] = ["*"], where: Optional[str] = None, 
               params: Optional[tuple] = None) -> List[Dict]:
        """
        查询数据
        :param table: 表名
        :param columns: 要查询的列名列表
        :param where: WHERE条件语句
        :param params: WHERE条件参数
        :return: 查询结果列表
        """
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table}"
        if where:
            query += f" WHERE {where}"
        return self.execute_query(query, params)

    def update(self, table: str, data: Dict, where: str, params: Optional[tuple] = None) -> int:
        """
        更新数据
        :param table: 表名
        :param data: 要更新的数据字典 {列名: 新值}
        :param where: WHERE条件语句
        :param params: WHERE条件参数
        :return: 受影响的行数
        """
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        return self.execute_update(query, tuple(data.values()) + (params or ()))

    def delete(self, table: str, where: str, params: Optional[tuple] = None) -> int:
        """
        删除数据
        :param table: 表名
        :param where: WHERE条件语句
        :param params: WHERE条件参数
        :return: 受影响的行数
        """
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute_update(query, params)

    def __enter__(self):
        """支持with语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.close()

