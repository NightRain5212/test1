from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from database import DatabaseManager
from datetime import datetime, timedelta
from passlib.context import CryptContext #用于密码哈希和验证
import secrets #用于生成安全的随机令牌

# 创建实例化对象
app = FastAPI()
db_manager = DatabaseManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 用于密码哈希和验证

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
    )

    # 验证刷新令牌是否匹配
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
    new_access_token = generate_access_token(user_id)
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

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 3600
    }

# 辅助函数：生成安全的随机令牌
def generate_secure_token(length=64):
    return secrets.token_urlsafe(length)

# 辅助函数：生成访问令牌(JWT)
def generate_access_token(user_id):
    # 示例：使用 JWT 生成访问令牌
    from jose import jwt
    secret_key = "your_secret_key"  # 替换为实际密钥
    algorithm = "HS256"
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=3600)
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)

# 传入用户信息，包含用户名，邮箱（可以为空），密码，在数据库中注册
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    # 检查用户名是否已存在
    existing_user = db_manager.select("users", where="username = %s", params=(request.username,))
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 插入新用户数据
    hashed_password = pwd_context.hash(request.password)  # 对密码进行哈希处理
    db_manager.insert("users", {
        "username": request.username,
        "email": request.email,
        "password": hashed_password
    })

    return {"message": "用户注册成功"}

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
        "created_date": user[0].get("created_date")
    }
    return user_info



