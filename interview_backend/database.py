import pymysql,dotenv,os,re
from datetime import date

# 加载环境变量
dotenv.load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")

timeout = 20

# # 连接数据库
# try:
#     # 获取一个数据库操作游标
#     cursor = connection.cursor()
#     cursor.execute("SELECT VERSION()")
#     result = cursor.fetchone()
#     print(result)
# finally:
#   cursor.close()
#   connection.close()


def is_valid_email(email):
    """
    验证邮箱格式是否正确
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def is_valid_password(password):
    """
    验证密码是否不少于6位且包含至少一个字母
    """
    
    # 检查密码是否至少6位
    if len(password) < 6:
        return False
    
    # 使用正则表达式检查密码是否包含至少一个字母
    if not re.search(r'[a-zA-Z]', password):
        return False
    
    return True

# 创建用户
def create_user(username,password,email,is_active = False):
    '''
    用于在数据库创建用户\n
    @params：\n
    @username 用户名\n
    @password 密码\n
    @email 邮箱\n
    @is_active 是否激活\n
    @return:\n
    @0 成功创建\n
    @1 意外错误\n
    @2 用户已存在\n
    @3 邮箱不合法\n
    @4 密码不合法\n
    '''
    connection = None
    cursor = None
    # 检查参数合法
    if(not is_valid_email(email)):
        return 3
    if(not is_valid_password(password)):
        return 4

    try:
      # 建立连接实例
      connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=DB_NAME,
        host= DB_HOST,
        password=DB_PASSWORD,
        read_timeout=timeout,
        port=int(DB_PORT),
        user=DB_USER,
        write_timeout=timeout,
      )
        
      cursor = connection.cursor()

      # 检查用户名是否已存在
      cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
      result = cursor.fetchone()
      print(f"查询结果: {result}")

      # 确保查询结果是一个字典，且包含 'COUNT(*)' 键
      if result and 'COUNT(*)' in result:
          count = result['COUNT(*)']  # 获取 COUNT(*) 的结果
      else:
          print("查询结果不合法，返回的不是预期的格式")
          return 1

      if count > 0:
          # 如果用户名已存在，抛出错误
          print(f"错误: 用户名 '{username}' 已存在！")
          return 2
      
      # 获取日期
      createdate = date.today()
      # 插入语句
      sql = '''
            INSERT INTO `users` (username,password,email,is_active,created_date)
            VALUES (%s,%s,%s,%s,%s)
            '''
      # 执行
      cursor.execute(sql,(username,password,email,is_active,createdate))
      # 提交事务
      connection.commit()
      print(f"用户{username}创建成功！")
      cursor.close()
      return 0
    except pymysql.MySQLError as e:
       cursor.close()
       print(f"报错{e}")
       return 1
    finally:
        if cursor:
          cursor.close()
        if connection:
          connection.close()

# 删除用户
def delete_user(username):
    '''
    用于在数据库删除用户\n
    @params：\n
    @username 用户名\n
    @return:\n
    @0 成功删除\n
    @1 意外错误\n
    @2 用户不存在\n
    '''
    connection = None
    cursor = None
    try:
        # 建立连接实例
        connection = pymysql.connect(
          charset="utf8mb4",
          connect_timeout=timeout,
          cursorclass=pymysql.cursors.DictCursor,
          db=DB_NAME,
          host= DB_HOST,
          password=DB_PASSWORD,
          read_timeout=timeout,
          port=int(DB_PORT),
          user=DB_USER,
          write_timeout=timeout,
        )
          
        cursor = connection.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and result['COUNT(*)'] == 0:
            print(f"错误: 用户 '{username}' 不存在！")
            return 2
        
        # 删除用户
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))

        # 提交事务到数据库
        connection.commit()

        print(f"用户 '{username}' 已成功删除！")
        return 0
    except pymysql.MySQLError as e:
        print(f"报错{e}")
        return 1
    finally:
        if cursor:
          cursor.close()
        if connection:
          connection.close()

def update_user_password(username,password):
    '''
    用于更新用户密码：\n
    @params：\n
    @username 用户名\n
    @password 密码\n
    @email 邮箱\n
    @return:\n
    @0 成功更新\n
    @1 意外错误\n
    @2 用户不存在\n
    @3 密码不合法\n
    '''
    connection = None
    cursor = None
    # 检查参数合法
    if(not is_valid_password(password)):
        return 3

    try:
        # 建立连接实例
        connection = pymysql.connect(
          charset="utf8mb4",
          connect_timeout=timeout,
          cursorclass=pymysql.cursors.DictCursor,
          db=DB_NAME,
          host= DB_HOST,
          password=DB_PASSWORD,
          read_timeout=timeout,
          port=int(DB_PORT),
          user=DB_USER,
          write_timeout=timeout,
        )
          
        cursor = connection.cursor()
        # 检查用户是否存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and result['COUNT(*)'] == 0:
            print(f"错误: 用户 '{username}' 不存在！")
            return 2
        
        # 更新用户信息
        sql = """
        UPDATE users
        SET password = %s
        WHERE username = %s
        """
        
        cursor.execute(sql, (password, username))

        # 提交事务到数据库
        connection.commit()
        print(f"用户 '{username}' 的信息已成功更新！")
        return 0
    
    except pymysql.MySQLError as e:
        print( f"数据库错误: {e}")  # 数据库错误
        return 1

    finally:
        # 关闭游标和连接
        if cursor:
          cursor.close()
        if connection:
          connection.close()

def update_user_email(username,email):
    '''
    用于更新用户邮箱：\n
    @params：\n
    @username 用户名\n
    @password 密码\n
    @email 邮箱\n
    @return:\n
    @0 成功更新\n
    @1 意外错误\n
    @2 用户不存在\n
    @3 邮箱不合法\n
    '''
    connection = None
    cursor = None
    # 检查参数合法
    if(not is_valid_email(email)):
        return 3

    try:
        # 建立连接实例
        connection = pymysql.connect(
          charset="utf8mb4",
          connect_timeout=timeout,
          cursorclass=pymysql.cursors.DictCursor,
          db=DB_NAME,
          host= DB_HOST,
          password=DB_PASSWORD,
          read_timeout=timeout,
          port=int(DB_PORT),
          user=DB_USER,
          write_timeout=timeout,
        )
          
        cursor = connection.cursor()
        # 检查用户是否存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and result['COUNT(*)'] == 0:
            print(f"错误: 用户 '{username}' 不存在！")
            return 2
        
        # 更新用户信息
        sql = """
        UPDATE users
        SET email = %s
        WHERE username = %s
        """
        
        cursor.execute(sql, (email, username))

        # 提交事务到数据库
        connection.commit()
        print(f"用户 '{username}' 的信息已成功更新！")
        return 0
    
    except pymysql.MySQLError as e:
        print( f"数据库错误: {e}")  # 数据库错误
        return 1

    finally:
        # 关闭游标和连接
        if cursor:
          cursor.close()
        if connection:
          connection.close()

def activate_user(username):
    '''
    用于激活账户\n
    @params：\n
    @username 用户名\n
    @return:\n
    @0 成功更新\n
    @1 意外错误\n
    @2 用户不存在\n
    '''
    connection = None
    cursor = None

    try:
        # 建立连接实例
        connection = pymysql.connect(
          charset="utf8mb4",
          connect_timeout=timeout,
          cursorclass=pymysql.cursors.DictCursor,
          db=DB_NAME,
          host= DB_HOST,
          password=DB_PASSWORD,
          read_timeout=timeout,
          port=int(DB_PORT),
          user=DB_USER,
          write_timeout=timeout,
        )
          
        cursor = connection.cursor()
        # 检查用户是否存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and result['COUNT(*)'] == 0:
            print(f"错误: 用户 '{username}' 不存在！")
            return 2
        
        # 更新用户信息
        sql = """
        UPDATE users
        SET is_active = true
        WHERE username = %s
        """
        
        cursor.execute(sql, (username))

        # 提交事务到数据库
        connection.commit()
        print(f"用户 '{username}' 的信息已成功更新！")
        return 0
    
    except pymysql.MySQLError as e:
        print( f"数据库错误: {e}")  # 数据库错误
        return 1

    finally:
        # 关闭游标和连接
        if cursor:
          cursor.close()
        if connection:
          connection.close()

def freeze_user(username):
    '''
    冻结用户\n
    @params：\n
    @username 用户名\n
    @return:\n
    @0 成功更新\n
    @1 意外错误\n
    @2 用户不存在\n
    '''
    connection = None
    cursor = None

    try:
        # 建立连接实例
        connection = pymysql.connect(
          charset="utf8mb4",
          connect_timeout=timeout,
          cursorclass=pymysql.cursors.DictCursor,
          db=DB_NAME,
          host= DB_HOST,
          password=DB_PASSWORD,
          read_timeout=timeout,
          port=int(DB_PORT),
          user=DB_USER,
          write_timeout=timeout,
        )
          
        cursor = connection.cursor()
        # 检查用户是否存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and result['COUNT(*)'] == 0:
            print(f"错误: 用户 '{username}' 不存在！")
            return 2
        
        # 更新用户信息
        sql = """
        UPDATE users
        SET is_active = false
        WHERE username = %s
        """
        
        cursor.execute(sql, (username))

        # 提交事务到数据库
        connection.commit()
        print(f"用户 '{username}' 的信息已成功更新！")
        return 0
    
    except pymysql.MySQLError as e:
        print( f"数据库错误: {e}")  # 数据库错误
        return 1

    finally:
        # 关闭游标和连接
        if cursor:
          cursor.close()
        if connection:
          connection.close()

def isactive(username):
    '''
    返回用户是否激活
    用于激活账户\n
    @params：\n
    @username 用户名\n
    @return:\n
    @0 冻结状态\n
    @1 激活状态\n
    @2 用户不存在\n
    @3 意外错误\n

    '''
    connection = None
    cursor = None

    try:
        # 建立连接实例
        connection = pymysql.connect(
          charset="utf8mb4",
          connect_timeout=timeout,
          cursorclass=pymysql.cursors.DictCursor,
          db=DB_NAME,
          host= DB_HOST,
          password=DB_PASSWORD,
          read_timeout=timeout,
          port=int(DB_PORT),
          user=DB_USER,
          write_timeout=timeout,
        )
          
        cursor = connection.cursor()
        # 检查用户是否存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and result['COUNT(*)'] == 0:
            print(f"错误: 用户 '{username}' 不存在！")
            return 2
        
        # 更新用户信息
        sql = """
        SELECT is_active
        FROM users
        WHERE username = %s
        """
        
        cursor.execute(sql, (username))
        user_data = cursor.fetchone()

        if user_data:
            # 返回用户是否激活状态
            return user_data['is_active']  # 如果返回的是 1，则代表激活，0 则代表未激活

    
    except pymysql.MySQLError as e:
        print( f"数据库错误: {e}")  # 数据库错误
        return 3

    finally:
        # 关闭游标和连接
        if cursor:
          cursor.close()
        if connection:
          connection.close()

def user_info(username):
    '''
    查询用户信息\n
    @params：\n
    @username 用户名\n
    @return:\n
    @user_data 类型：dict \n
    @1 意外错误\n
    @2 用户不存在\n
    '''
    connection = None
    cursor = None
    try:
      # 建立连接实例
      connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=DB_NAME,
        host= DB_HOST,
        password=DB_PASSWORD,
        read_timeout=timeout,
        port=int(DB_PORT),
        user=DB_USER,
        write_timeout=timeout,
      )
        
      cursor = connection.cursor()
      # 检查用户是否存在
      cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
      result = cursor.fetchone()

      if result and result['COUNT(*)'] == 0:
          print(f"错误: 用户 '{username}' 不存在！")
          return 2
      
      # 查询并返回用户的详细信息
      cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
      user_data = cursor.fetchone()

      if user_data:
          # 返回用户信息字典
          return user_data


    except pymysql.MySQLError as e:
      print( f"数据库错误: {e}")  # 数据库错误
      return 1

    finally:
        # 关闭游标和连接
        if cursor:
          cursor.close()
        if connection:
          connection.close()

print(create_user("123","a1234567","111@qq.com"))
