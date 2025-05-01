# 开发者文档   

## 前端

- 运行
- npm install
- npm run dev
- push前（如果安装了新的东西忘记使用--save）
- npm list,然后把输出结果和 package.json 一起提交给ai处理

## 数据库连接   

- aiven 数据库MySQL
- 依赖：

python -m pip install pymysql
python -m pip install cryptography

- users表单关键字

- id
- username 4~30 位,字母、汉字、数字、连字符（-），不能以数字开头，不能包含空格
- password 8~12 位 字母、数字、特殊字符（!@#$%^&*()_+）,至少包含字母和数字，不能包含空格和汉字
- email
- created_date
- is_active

## 后端服务器

- FASTAPI
- 运行：`fastapi dev main.py`

## 接口  

- /api/auth/refresh  发送refresh_token获取新的access_token和refresh_token
- /api/auth/login   注册登录用户信息列表
- /api/user/get_info  根据提供的信息查询用户信息,这里现在只给username  
- /api/auth/register 给出用户名和密码等，注册用户

## 开发阶段

1. 初期构建项目框架，实现简单的登录全功能
2. 预：一边优化前端页面，优化性能，一般纵向拓展功能

## 功能目标

1.主体有开始面试，分为单人模式和双人模式。单人模式下，可以选择是否开启录音或录像，是否开启ai自动提问。多人模式下，由一人充当面试官，可以借助内置ai或者记录生成问题来提问，并且可以随时对记录的信息增改，实时观看可视化结果和分析结果以及ai建议，另一人选择坐在或站在电脑后，正对屏幕，回答问题，系统可以自动分辩说话者。

2.社区功能。可以查看在线面试题目或者实时面试帖子，或者跳转相关网站，或者根据专业推荐相关网站或备战资源。

3.可以发布面试经验贴，查看他人帖子。

4.可以导入校园社区，区分学长校友，咨询获得建议。

## 问题

1 后端缺乏对应函数

2.python项目需要补充requirements.txt文件，否则手动安装依赖。

3.考虑使虚拟环境
