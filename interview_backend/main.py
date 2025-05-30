from dotenv import load_dotenv
import os  # 用于获取环境变量
import subprocess
import sys
import shutil
from pathlib import Path

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
from typing import Optional

from passlib.context import CryptContext #用于密码哈希和验证
import secrets  #用于生成安全的随机令牌
from jose import jwt #jwt相关

# 导入分析器
from analyzer.main import InterviewAnalyzer
from config import UPLOAD_DIR, TEMP_DIR, VIDEO_DIR, AUDIO_DIR, UPLOAD_CONFIG

# 创建分析器实例
from analyzer.main import InterviewAnalyzer
from config import UPLOAD_DIR, TEMP_DIR, VIDEO_DIR, AUDIO_DIR, UPLOAD_CONFIG

# 创建分析器实例
analyzer = InterviewAnalyzer()

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
load_dotenv()  # 先加载原始 .env
print(">>>>>>>>>>>>>>>>>>>>>加载环境变量<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES =int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

# analyzer.run()#测试

# 定义 Pydantic 模型
class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    username: str
    email: str =None
    password: str

class UserInfoRequest(BaseModel):
    username: str

# 定义视频分析请求模型
class VideoAnalysisRequest(BaseModel):
    video_path: str
    resume_text: str = ""  # 可选的简历文本

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
        return {"data": "注册成功"}
    except Exception as e:
        print("注册失败:", e)
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
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expired_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60*1000#  毫秒
        }
    }    
    print("返回响应:", res)
    return res
# 传入查询参数，至少会包括用户名
@app.get("/api/user/get_info")
async def get_info(username: str):
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
    user_info = {
        "username": user[0]["username"],
        "email": user[0]["email"],
        "password": user[0]["password"],  # 注意：实际不应返回密码字段
        "created_data": user[0]["created_data"].strftime("%Y-%m-%d") if user[0]["created_data"] else None #转换日期格式
    }
    print(user_info)
    res={"data": user_info}
    print("返回用户信息:", res)
    return res

# 文件上传处理
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        print(f"开始处理文件上传: {file.filename}")
        
        # 检查文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        print(f"文件扩展名: {file_extension}")
        
        if file_extension not in UPLOAD_CONFIG["allowed_extensions"]:
            print(f"不支持的文件类型: {file_extension}")
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。支持的类型: {', '.join(UPLOAD_CONFIG['allowed_extensions'])}"
            )
        
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 检查文件大小
        if file_size > UPLOAD_CONFIG["max_file_size"]:
            print(f"文件太大: {file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制: {UPLOAD_CONFIG['max_file_size'] / 1024 / 1024}MB"
            )
        
        # 生成唯一文件名
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}{file_extension}"
        print(f"生成的文件名: {unique_filename}")
        
        # 根据文件类型选择存储目录
        if file_extension in [".mp4", ".avi", ".mov", ".webm"]:
            save_dir = VIDEO_DIR
        elif file_extension in [".wav", ".mp3"]:
            save_dir = AUDIO_DIR
        else:
            save_dir = UPLOAD_DIR
            
        print(f"保存目录: {save_dir}")
        
        # 确保目录存在
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = save_dir / unique_filename
        print(f"完整文件路径: {file_path}")
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        print(f"文件上传成功: {file_path}")
        
        return {
            "data": {
                "filename": unique_filename,
                "filepath": str(file_path)
            }
        }
        
    except HTTPException as e:
        print(f"HTTP异常: {str(e)}")
        raise e
    except Exception as e:
        print(f"上传过程中出现错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )
    finally:
        await file.close()

# 挂载静态文件目录
app.mount("/videos", StaticFiles(directory=str(VIDEO_DIR), check_dir=False), name="videos")
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR), check_dir=False), name="audio")

# 获取视频文件
@app.get("/api/video/{filename}")
async def get_video(filename: str):
    try:
        # 清理文件名，只保留基本文件名
        clean_filename = Path(filename).name
        video_path = VIDEO_DIR / clean_filename
        
        print(f"请求视频文件: {clean_filename}")
        print(f"完整路径: {video_path}")
        
        if not video_path.exists():
            print(f"文件不存在: {video_path}")
            raise HTTPException(status_code=404, detail="视频文件不存在")
            
        return FileResponse(str(video_path))
    except Exception as e:
        print(f"获取视频失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取视频失败: {str(e)}")

# 分析视频
@app.post("/api/analyze/video")
async def analyze_video(request: VideoAnalysisRequest):
    """
    分析面试视频接口
    """
    try:
        print(f"收到分析请求，视频路径: {request.video_path}")
        
        # 清理和验证文件名
        filename = Path(request.video_path).name
        if not filename:
            raise HTTPException(
                status_code=400,
                detail="无效的文件名"
            )
            
        # 构建完整的文件路径
        video_path = VIDEO_DIR / filename
        print(f"完整文件路径: {video_path}")
        print(f"文件是否存在: {video_path.exists()}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"视频目录内容: {list(VIDEO_DIR.glob('*'))}")
        
        if not video_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"视频文件不存在: {filename}"
            )
            
        # 如果提供了简历文本，更新分析器的简历文本
        if request.resume_text:
            analyzer.resume_text = request.resume_text
            
        print(f"开始分析视频: {video_path}")
        
        # 执行分析
        try:
            result = analyzer.analyze_interview(str(video_path))
            print("分析完成，返回结果")
            return {
                "data": result,
                "message": "分析完成"
            }
        except Exception as e:
            print(f"分析过程出错: {str(e)}")
            print(f"错误类型: {type(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"视频分析失败: {str(e)}"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"处理请求失败: {str(e)}"
        )

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

