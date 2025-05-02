import dotenv  # 用于加载环境变量
import os  # 用于获取环境变量

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from database import DatabaseManager

from datetime import datetime, timedelta #timedelta类可以参与datatime的加减
from typing import Optional

from passlib.context import CryptContext #用于密码哈希和验证
import secrets #用于生成安全的随机令牌
#jwt相关
from jose import jwt

# 创建实例化对象
app = FastAPI()
db_manager = DatabaseManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 用于密码哈希和验证
# 配置JWT
dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# 定义 Pydantic 模型
class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    username: str
    email: str = None
    password: str

class UserInfoRequest(BaseModel):
    username: str
# 传入刷新令牌，获取新的访问令牌 access_token 和 刷新令牌 refresh_token
@app.post("/api/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    current_refresh_token = request.refresh_token

    # 从数据库获取令牌记录（包括哈希值和元数据）
    token_record = db_manager.select(
        "refresh_tokens",
        where="is_active = TRUE AND expires_at > %s",
        params=(datetime.utcnow(),)
    ) # %s是占位符，用于后面的params

    # 验证刷新令牌是否匹配
    #next(iterator,default=None)获取迭代器的下一个元素
    #从token_record（这里是一张表）中找到第一个匹配的记录，如果没有找到则返回None
    token_record = next(
        (record for record in token_record if pwd_context.verify(current_refresh_token, record["token_hash"])),
        None
    )

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌或已过期"
        )

    user_id = token_record["user_id"]

    # 生成新令牌
    new_access_token = generate_access_token({"sub": str(user_id)})
    new_refresh_token = generate_secure_token()

    # 更新数据库（使用事务确保原子性）
    try:
        db_manager.update(
            "refresh_tokens",
            {
                "is_active": False,
                "revoked_at": datetime.utcnow(),
                "last_used_at": datetime.utcnow()
            },
            "id = %s",
            (token_record["id"],)
        )

        db_manager.insert(
            "refresh_tokens",
            {
                "user_id": user_id,
                "token_hash": pwd_context.hash(new_refresh_token),
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "is_active": True
            }
        )

        db_manager.commit()
    except Exception as e:
        db_manager.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌更新失败"
        )

    #FastApi自动将类型转换为json格式
    return {
        "data":{
         "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60 # 访问令牌的有效期
         }
    }

# 辅助函数：生成安全的随机令牌
def generate_secure_token(length=64):
    return secrets.token_urlsafe(length)

# 辅助函数：生成访问令牌(JWT),data是一个字典，包含要编码的数据（选择要唯一）
def generate_access_token(data: dict, expires_delta: Optional[timedelta] = None):#None或者timedelta
    to_encode = data.copy()#创建副本，避免直接修改原始数据
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})#更新字典的exp键
    #传入三个参数：要封装的数据，加密密钥，加密算法
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 传入用户信息，包含用户名，邮箱（可以为空），密码，在数据库中注册
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    # 检查用户名是否已存在
    existing_user = db_manager.select("users", where="username = %s", params=(request.username,))
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 插入新用户数据
    try:
        db_manager.insert("users", {
            "username": request.username,
            "email": request.email,
            "password": request.password
        })
        return {"data":"注册成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="用户注册失败")

#返回令牌，更新用户状态，刷新令牌
@app.post("/api/auth/login")
async def login(request: RegisterRequest):
    # 1. 验证用户是否存在
    users = db_manager.select(
        "users", 
        where="username = %s", 
        params=(request.username,)
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"  # 模糊提示，避免暴露用户存在信息
        )
    
    user = users[0]
    
    # 2. 验证密码
    if not pwd_context.verify(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 3. 生成令牌
    access_token = generate_access_token({"sub": str(user["id"])})
    refresh_token = generate_secure_token()
    
    # 4. 保存刷新令牌到数据库
    try:
        db_manager.insert(
            "refresh_tokens",
            {
                "user_id": user["id"],
                "token_hash": pwd_context.hash(refresh_token),
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "is_active": True
            }
        )
        db_manager.commit()
    except Exception as e:
        db_manager.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请重试"
        )
    
    # 5. 返回响应
    return {
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    }

# 传入 userinfo, 至少会包括用户名
@app.get("/api/user/get_info")
async def get_info(request: UserInfoRequest):
    # 查询用户信息
    user = db_manager.select("users", where="username = %s", params=(request.username,))
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")

    # 返回用户信息（隐藏敏感信息，如密码）
    user_info = {
        "username": user[0]["username"],
        "email": user[0]["email"],
        "password":user[0]["password"],
        "created_date": user[0].get("created_date")
    }
    return {"data":user_info}



