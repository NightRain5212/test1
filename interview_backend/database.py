import pymysql  # 用于连接MySQL数据库
import dotenv  # 用于加载环境变量
import os  # 用于获取环境变量
from typing import Dict, List, Optional, Union,Any  # 导入类型提示
#数据库：username/password/email/created_data(data类型)
class DatabaseManager:
    def __init__(self):
        """初始化数据库连接"""
        dotenv.load_dotenv()
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_NAME =os.getenv("DB_NAME")  # 可以改为从环境变量读取
        self.timeout = 20
        
        self.connection = None
        self.connect()
        #self.test_connection()
        

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
        #raise关键字用于保持异常链完整，或传递异常

    def test_connection(self):
        """测试数据库连接并输出关键信息"""
        print("✓ 开始数据库连接测试-------------------------------------------")
        try:
            if not self.connection or not self.connection.open:
                self.connect()

            with self.connection.cursor() as cursor:
                # 1. 输出连接URL（隐藏密码）
                safe_url = f"mysql://{self.DB_USER}:***@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                print(f"✓ 连接URL: {safe_url}")

                # 2. 检查服务器版本
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()["VERSION()"]
                print(f"✓ MySQL服务器版本: {version}")

                # 3. 检查当前用户权限
                cursor.execute(f"SHOW GRANTS FOR CURRENT_USER")
                grants = cursor.fetchall()
                print("\n✓ 用户权限:")
                for grant in grants:
                    print(f"  - {grant['Grants for {}@%'.format(self.DB_USER)]}")

                # 4. 检查数据库是否存在
                cursor.execute("SHOW DATABASES LIKE %s", (self.DB_NAME,))
                db_exists = cursor.fetchone()
                print(f"\n✓ 数据库状态: {'存在' if db_exists else '不存在'}")

                # 5. 测试基本查询
                cursor.execute("SELECT 1 AS connection_test")
                test_result = cursor.fetchone()
                print(f"✓ 连接测试: {'成功' if test_result['connection_test'] == 1 else '失败'}")

                # 6. 检查SSL状态
                cursor.execute("SHOW STATUS LIKE 'Ssl_cipher'")
                ssl_status = cursor.fetchone()
                print(f"✓ SSL加密: {'启用' if ssl_status['Value'] else '未启用'}")

                return True

        except pymysql.MySQLError as e:
            print(f"✗ 连接测试失败: {e}")
            # 特别处理权限错误
            if e.args[0] == 1044:
                print("  可能原因: 用户缺少数据库权限，请执行:")
                print(f"  GRANT ALL PRIVILEGES ON {self.DB_NAME}.* TO '{self.DB_USER}'@'%';")
            elif e.args[0] == 1045:
                print("  可能原因: 用户名或密码错误")
            return False

    def commit(self):
        """
        提交当前事务
        将当前事务中的所有操作永久保存到数据库
        """
        if self.connection:
            try:
                self.connection.commit()
                print("Transaction committed")
            except pymysql.MySQLError as e:
                print(f"Error committing transaction: {e}")
                raise

    def rollback(self):
        """
        回滚当前事务
        撤销当前事务中的所有未提交操作
        """
        if self.connection:
            try:
                self.connection.rollback()
                print("Transaction rolled back")
            except pymysql.MySQLError as e:
                print(f"Error rolling back transaction: {e}")
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

    def select(self, table: str, columns: List[str] = ["*"], where: Optional[str] = None, #optional等价于None或list[str]
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

