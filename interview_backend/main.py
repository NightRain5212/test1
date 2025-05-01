from fastapi import FastAPI

# 创建实例化对象
app = FastAPI()

# 定义路径装饰器
# 请求路径:/  请求：get
@app.get("/")
# 路径操作函数，使用get访问/路径时被调用，异步函数节省时间
async def root() :
    return {"message":"hello world!"}
#传入刷新令牌，获取新的访问令牌
@app.post("/api/auth/refresh")
async def refreshToken(refresh_token:str):
    return {"message":"hello world!"}

@app.post("/api/auth/login")
async def login(username:str):
    return {"message":"hello world!"}

@app.post("/api/auth/register")
async def register(userinfo:json):
    return {"message":"hello world!"}

#userinfo:json  包括username,email,password等信息
@app.post("/api/user/get_info")
async def get_info(userinfo:json):
    return {"message":"hello world!"}

# ai参考代码：
# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime, timedelta
# import jwt
# from passlib.context import CryptContext

# app = FastAPI()

# # 安全配置
# SECRET_KEY = "your-secret-key-here"  # 生产环境请使用更安全的密钥
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
# REFRESH_TOKEN_EXPIRE_DAYS = 7

# # 密码哈希
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # 模拟数据库
# fake_users_db = {
#     "testuser": {
#         "username": "testuser",
#         "email": "test@example.com",
#         "hashed_password": pwd_context.hash("testpass"),
#         "disabled": False,
#     }
# }

# # 模型定义
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#     refresh_token: str

# class TokenData(BaseModel):
#     username: Optional[str] = None

# class User(BaseModel):
#     username: str
#     email: Optional[str] = None
#     disabled: Optional[bool] = None

# class UserInDB(User):
#     hashed_password: str

# class UserCreate(BaseModel):
#     username: str
#     email: str
#     password: str

# class RefreshToken(BaseModel):
#     refresh_token: str

# # 工具函数
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)

# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(days=7)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl


