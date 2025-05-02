# 数据库连接    

- aiven 数据库MySQL
- 依赖：

python -m pip install pymysql
python -m pip install cryptography

- users表单关键字

- id
- username 4~30 位,字母、汉字、数字、连字符（-），不能以数字开头，不能包含空格
- password 8~12 位 字母、数字、特殊字符（!@#$%^&*()_+）,至少包含字母和数字，不能包含空格和汉字
- email 最长50个字符，也可以没有
- created_data

# 后端服务器

- FASTAPI
- 运行：`fastapi dev main.py`

不要忽略.env，密码屏蔽
