from dotenv import load_dotenv
import os  # 用于获取环境变量
import subprocess
import sys
import shutil
from pathlib import Path
import uuid
import json
# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from fastapi import FastAPI, HTTPException, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import DatabaseManager

from datetime import datetime, timedelta #timedelta类可以参与datatime的加减
from typing import Optional,Dict,Any

from passlib.context import CryptContext #用于密码哈希和验证
import secrets  #用于生成安全的随机令牌
from jose import jwt #jwt相关

from analyzer import main as analyzer #导入模块
from  FileManager import FileManager
# 创建实例化对象
print(">>>>>>>>>>>>>>>>>>>>>加载对象实例<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_manager = DatabaseManager()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 用于密码哈希和验证
# 配置JWT
load_dotenv(".env")  # 先加载原始 .env
load_dotenv(".env.secret")
print(">>>>>>>>>>>>>>>>>>>>>加载环境变量<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES =int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")

file_manager = FileManager(OSS_ACCESS_KEY_ID,OSS_ACCESS_KEY_SECRET,"interviewresource","https://cn.aliyun.com/")

#analyzer.run("demo-video.mp4")#测试
#analyzer.run()#测试

# 定义 Pydantic 模型
class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    username: str
    email: str =None
    password: str

class UserInfoRequest(BaseModel):
    id: int
    username: str

# 定义历史记录数据模型（如果需要）
class HistoryRecord(BaseModel):
    id: int
    user_id: int
    action: str
    timestamp: datetime
class UploadRequest(BaseModel):
    video: Optional[UploadFile] = File(None)
    audio: Optional[UploadFile] = File(None)
    image: Optional[UploadFile] = File(None)
class UpdataRequest(BaseModel):
    id: int
    username: str=""
    email: str=""
    preferences: Dict[str, Any] = {} #user_store中直接存储json

# 传入刷新令牌，获取新的访问令牌access_token和刷新令牌refresh_token
@app.post("/api/auth/refresh")
async def refresh_token(request: RefreshTokenRequest,meta:Request):
    current_refresh_token = request.refresh_token

    # 从数据库获取令牌记录（包括哈希值和元数据）
    token_record = db_manager.select(
        table="refresh_tokens",
        conditions={
            "is_active":1,
            "ip_address":meta.client.host, #获取客户端IP地址
            "expired_at":{">":datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
        }
    )

    # 验证刷新令牌是否匹配
    # next(iterator,default=None)获取迭代器的下一个元素
    # 从token_record（这里是一张表）中找到第一个匹配的记录，如果没有找到则返回None
    token_record = next(
        (record for record in token_record if pwd_context.verify(current_refresh_token, record["token_hash"])),
        None
    )

    if not token_record:
        print("无效的刷新令牌或已过期")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌或已过期"
        )

    user_id = token_record["user_id"]
    # 生成新令牌
    new_access_token = generate_access_token({"sub": str(user_id)})

    # 更新数据库（使用事务确保原子性）
    try:
        db_manager.update(
            table="refresh_tokens",
            data={
                "user_id": user_id,
                "token": refresh_token,
                "token_hash": pwd_context.hash(refresh_token),
                "is_active": 1,
                "ip_address":meta.client.host, #获取客户端IP地址
                "created_at":token_record["created_at"],
                "expired_at":token_record["expired_at"]
            },
            conditions={"id": token_record["id"]}
        )
        db_manager.commit()
    except Exception as e:
        db_manager.rollback()
        print(f"令牌更新失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌更新失败"
        )

    # FastAPI自动将类型转换为json格式
    return {
        "data": {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 访问令牌的有效期
        }
    }
# 辅助函数：生成安全的随机令牌,封装过期时间
def generate_refresh_token(user_id, length=64):
    # 生成随机部分
    token_id = secrets.token_urlsafe(length)

    #计算时间
    data = datetime.utcnow()
    expired = data + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    # 格式化为 "YYYY-MM-DD HH:MM:SS" 格式
    data = data.strftime("%Y-%m-%d %H:%M:%S")
    expired= expired.strftime("%Y-%m-%d %H:%M:%S")

    # 组合 payload（包含过期时间）
    payload = {
        "sub": user_id,
        "jti": token_id,  # token 唯一标识
        "exp": expired # 过期时间
    }
    
    token = jwt.encode(payload, "SECRET_KEY", algorithm=ALGORITHM )
    
    return {"token":token,"created_at":str(data),"expired_at":expired} 

# 辅助函数：生成访问令牌(JWT),data是一个字典，包含要编码的数据（选择要唯一）
def generate_access_token(data: dict, expires_delta: Optional[timedelta] = None):#None或者timedelta
    to_encode = data.copy()#创建副本，避免直接修改原始数据
    #datatime.utcnow()默认返回YYYY-MM-DD HH:MM:SS.microseconds格式的时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire=expire.strftime("%Y-%m-%d %H:%M:%S")#格式化为 "YYYY-MM-DD HH:MM:SS" 格式
    to_encode.update({"exp": expire})#更新字典的exp键
    #传入三个参数：要封装的数据，加密密钥，加密算法
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 传入用户信息，包含用户名，邮箱（可以为空），密码，在数据库中注册
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    # 检查用户名是否已存在
    print("注册:",request)
    existing_user = db_manager.select(
        table="users", 
        conditions={"username": request.username}
    )
    print("查询用户信息：",existing_user)
    if existing_user:
        return {"data": None}  # 返回None，不返回error

    # 插入新用户数据
    try:
        created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print("开始注册用户")
        db_manager.insert("users", {
            "username": request.username,
            "email": request.email,
            "password": request.password, # 注意：实际应用中应先哈希密码
            "created_data":created_at
        })
        db_manager.commit()
        return {"data": "注册成功"}
    except Exception as e:
        print("注册失败:", e)
        db_manager.rollback()
        raise HTTPException(status_code=500, detail="用户注册失败")

# 返回令牌，更新用户状态，刷新令牌
@app.post("/api/auth/login")
async def login(request: RegisterRequest,meta: Request):#request使用pydantic模型将json的body自动转换为字典，meta则直接继承原始json对象，用于获取body之外的内容
    print(">>>>>>>>>>>>>>>>>>>>>登录<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print("请求体：：", request)
    # 1. 验证用户是否存在
    users = db_manager.select(
        table="users",
        conditions={"username": request.username}
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"  # 模糊提示，避免暴露用户存在信息
        )
    
    user = users[0]
    print("登录用户:", user)
    # 2. 生成令牌
    access_token = generate_access_token({"sub": str(user["id"])})
    res=generate_refresh_token(user["id"])
    refresh_token = res["token"]
    print("access_token:", access_token)
    print("refresh_token:", refresh_token)
    # 3. 保存刷新令牌到数据库
    try:
        print("开始保存新令牌")
        print("user_id:", user["id"],"ip_address:",meta.client.host,"created_at:",res["created_at"],"expired_at:",res["expired_at"])
        db_manager.insert(
            table="refresh_tokens",
            data={
                "user_id": user["id"],
                "token": refresh_token,
                "token_hash": pwd_context.hash(refresh_token),
                "is_active": 1,
                "ip_address":meta.client.host, #获取客户端IP地址
                "created_at":res["created_at"],
                "expired_at":res["expired_at"]
            }
        )
        db_manager.commit()
    except Exception as e:
        print("新增令牌失败:", e)
        db_manager.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请重试"
        )
    
    # 4. 返回响应
    res={
        "data": {
            "id": user["id"],
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expired_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60*1000#  毫秒
        }
    }    
    print("返回响应:", res)
    return res
# 传入用户名，返回用户相关信息
@app.get("/api/user/get_info")
async def get_info(username: str):
    #自动转换json为词典
    def safe_get_json(field):
        if field is None:
            return None
        if isinstance(field, dict):  # 如果驱动已自动转换
            return field
        try:
            return json.loads(field)
        except (TypeError, json.JSONDecodeError):
            return None
    print(">>>>>>>>>>开始查询用户信息<<<<<<<<<<<<<<<<<")
    # 查询用户信息
    user = db_manager.select(
        table="users",
        conditions={"username": username}
    )
    if not user:
        print("用户不存在")
        return {"data": None}  # 如果没有找到用户，返回空字典，不返回error

    # 返回用户信息（隐藏敏感信息，如密码）
    print("用户存在")
    print(user)
    #查询用户存储信息
    user_store = db_manager.select(
        table="user_store",
        conditions={"user_id": user["id"]}
    )
    
    try:
        preference =safe_get_json(user_store[0]["user_preference"] if user_store else None)
    except Exception as e:
        print("解析用户偏好失败:", e)
        preference=None
    user_info = {
        "id": user[0]["id"],
        "username": user[0]["username"],
        "email": user[0]["email"],
        "password": user[0]["password"], 
        "created_data": user[0]["created_data"].strftime("%Y-%m-%d") if user[0]["created_data"] else None ,#转换日期格式
        "preference":preference,
    }
    print(user_info)

    res={"data": user_info}
    print("返回用户信息:", res)
    return res

# 查询历史记录的API端点
@app.get("/api/history")
async def get_history(user_id: int):
    try:
        # 从数据库中查询历史记录
        history_records = db_manager.select(
            table="history",
            conditions={"user_id": user_id}
        )
        if not history_records:
            return {"data": []}  # 返回空列表

        # 返回查询结果
        return {"data": history_records}
    except Exception as e:
        print("查询历史记录失败:", e)
        raise HTTPException(status_code=500, detail="查询历史记录失败")

# 保存分析结果到历史记录的API端点
@app.post("/api/history")
async def save_history(user_id: int, action: str, result: dict):
    # 检查并创建历史记录表
    table_exists = db_manager.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='history';
    """)

    if not table_exists:
        # 创建表
        db_manager.execute("""
            CREATE TABLE history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                result TEXT NOT NULL
            );
        """)
        db_manager.commit()

    try:
        # 插入分析结果到历史记录表
        db_manager.insert(
            table="history",
            data={
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "result": result
            }
        )
        db_manager.commit()
        return {"message": "历史记录保存成功"}
    except Exception as e:
        db_manager.rollback()
        print("保存历史记录失败:", e)
        raise HTTPException(status_code=500, detail="保存历史记录失败")

@app.post("/api/upload")
async def upload(request: UploadRequest):
    result = {}
    try:
        # 检查是否有文件上传
        if not any([request.video, request.audio, request.image]):
            return {
            "code": 400,
            "message": "没有要上传的文件",
            "data": None
            }

        # 处理视频文件
        if request.video and request.video.filename:
            video_ext = os.path.splitext(request.video.filename)[1]
            video_key = f"video/{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4().hex}{video_ext}"
            result["video_url"]= file_manager.upload_file(request.video.file, video_key)

        # 处理音频文件
        if request.audio and request.audio.filename:
            audio_ext = os.path.splitext(request.audio.filename)[1]
            audio_key = f"audio/{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4().hex}{audio_ext}"
            result["audio_url"]=file_manager.upload_file(request.audio.file, audio_key)

        # 处理图片文件
        if request.image and request.image.filename:
            image_ext = os.path.splitext(request.image.filename)[1]
            image_key = f"img/{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4().hex}{image_ext}"
            result["image_url"] =file_manager.upload_file(request.image.file, image_key)

        return {
            "code": 200,
            "message": "文件上传成功",
            "data": result
        }

    except Exception as e:
        print("文件上传失败:", e)
        return{
            "code": 500,
            "message": "文件上传失败",
            "data": None
        }

@app.post("/api/update")
async def update(request: UpdataRequest):
    #更新users表
    try:
        db_manager.update(
            table="users",
            data={
                "username": request.username,
                "email": request.email,
            },
            conditions={"id": request.id}
        )
        db_manager.commit()
    except Exception as e:
        print("更新user表失败:",e)
        db_manager.rollback()
    tmp_user = db_manager.select(
        table="users_store",
        conditions={"id": request.id}
    )
    #如果是首次更新
    if not tmp_user:
        try:
            db_manager.insert(
                table="user_store",
                data={
                    "user_id": request.id,
                    "user_preference": json.dumps(request.preference)  # 显式转换为JSON字符串
                }
            )
            db_manager.commit()
        except Exception as e:
            print("插入user_store表失败:",e)
            db_manager.rollback()
    else:
        #更新user_store表
        try:
            db_manager.update(
                table="user_store",
                data={
                    "user_preference": json.dumps(request.preference)  # 显式转换为JSON字符串
                },
                conditions={"id": request.id}
            )
            db_manager.commit()
        except Exception as e:
            print("更新user_store表失败:",e)
            db_manager.rollback()
    return {"message": "更新成功","data": ""}

# 如果通过命令fastapi dev main.py，则不会执行下面的代码
if __name__ == "__main__":
    # 使用 FastAPI CLI 启动应用
    subprocess.run([
        sys.executable,  # 当前 Python 解释器路径
        "-m", 
        "fastapi", 
        "dev", 
        "main.py",
        "--host", "0.0.0.0",
        "--port", os.getenv("PORT", "8000")
    ])

