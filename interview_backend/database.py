import pymysql,dotenv,os

# 加载环境变量
dotenv.load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")


timeout = 20
# 建立连接实例
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="users",
  host= DB_HOST,
  password=DB_PASSWORD,
  read_timeout=timeout,
  port=int(DB_PORT),
  user=DB_USER,
  write_timeout=timeout,
)
  

# 连接数据库
try:
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")
    result = cursor.fetchone()
    print(result)
finally:
  connection.close()