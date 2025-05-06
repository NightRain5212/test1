import pymysql  # 用于连接MySQL数据库
import dotenv  # 用于加载环境变量
import os  # 用于获取环境变量
import re # 用于正则表达式
from typing import Dict, List, Optional, Union,Any,Tuple # 导入类型提示
from contextlib import contextmanager  # 用于上下文管理器

#数据库：username/password/email/created_data(data类型)
class DatabaseManager:
    def __init__(self):
        """初始化数据库连接"""
        print("开始初始化数据库-----------------------------------------")
        dotenv.load_dotenv()
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_NAME =os.getenv("DB_NAME")  # 可以改为从环境变量读取
        self.timeout = 20
        
        self.connection = None
        print("开始连接数据库-----------------------------------------")
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
        """提交当前事务"""
        print("提交当前事务-------------------------------------------")
        try:
            self.connection.commit()
        except pymysql.MySQLError as e:
            print(f"  提交事务时发生错误: {e}")
            self.connection.rollback()
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
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Error executing query: {e}")
            raise

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """执行更新操作（安全参数化）"""
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params or ())
                self.connection.commit()
                return affected_rows
        except pymysql.MySQLError as e:
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