## 数据库连接

-  SQLPub数据库MySQL
- 依赖：
```
python -m pip install pymysql

```

- users表单关键字
    - username
    - password
    - email
    - created_date
    - is_active
    - 定义如下：
```mysql
    `username` VARCHAR(20) UNIQUE NOT NULL primary key,
    `password` VARCHAR(20) NOT NULL,
    `email` VARCHAR(50) NOT NULL,
    `is_active` BOOLEAN DEFAULT false,
    `created_date` DATE NOT NULL
```

## 后端服务器
- FASTAPI
- 运行：`fastapi dev main.py`

## 数据库接口
- `create_user(username,password,email,is_active = False)`
- `delete_user(username)`
- `update_user_password(username,password)`
- `update_user_email(username,email)`
- `user_info(username)`
- `activate_user(username)`
- `freeze_user(username)`
- `isactive(username)`