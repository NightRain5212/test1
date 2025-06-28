import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent
STORAGE_DIR = BASE_DIR / "interview_storage"  # 文件存储根目录

# 创建存储目录结构
UPLOAD_DIR = STORAGE_DIR / "uploads"  # 上传文件目录
TEMP_DIR = STORAGE_DIR / "temp"      # 临时文件目录
VIDEO_DIR = STORAGE_DIR / "videos"   # 视频文件目录
AUDIO_DIR = STORAGE_DIR / "audio"    # 音频文件目录

# 确保所有必要的目录都存在
for directory in [UPLOAD_DIR, TEMP_DIR, VIDEO_DIR, AUDIO_DIR, STORAGE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# FastAPI 配置
FASTAPI_CONFIG = {
    "title": "Interview Analysis API",
    "description": "面试分析系统API",
    "version": "1.0.0"
}

# 文件上传配置
UPLOAD_CONFIG = {
    "max_file_size": 1024 * 1024 * 100,  # 100MB
    "allowed_extensions": [".mp4", ".avi", ".mov", ".wav", ".mp3", ".webm"]
}

# 星火大模型配置
SPARK_CONFIG = {
    "app_id": os.getenv("SPARK_APP_ID", ""),
    "api_key": os.getenv("SPARK_API_KEY", ""),
    "api_secret": os.getenv("SPARK_API_SECRET", "")
}
# 星火大模型配置
SPARK_CONFIG1 = {
    "app_id": os.getenv("SPARK_APP_ID1", ""),
    "api_key": os.getenv("SPARK_API_KEY1", ""),
    "api_secret": os.getenv("SPARK_API_SECRET1", "")
}
# 检查星火大模型配置
def check_spark_config():
    """检查星火大模型配置是否完整"""
    missing_keys = []
    for key in ["app_id", "api_key", "api_secret"]:
        if not SPARK_CONFIG.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(
            f"星火大模型配置不完整，缺少以下环境变量：{', '.join(missing_keys)}\n"
            "请确保在 .env 文件中设置了以下变量：\n"
            "SPARK_APP_ID=你的应用ID\n"
            "SPARK_API_KEY=你的API密钥\n"
            "SPARK_API_SECRET=你的API密钥"
        )
    
    print("星火大模型配置检查通过")
    print(f"- AppID: {SPARK_CONFIG['app_id']}")
    print(f"- API Key: {SPARK_CONFIG['api_key'][:8]}...")

# 在导入时检查配置
check_spark_config()

# 文件上传配置
ALLOWED_EXTENSIONS = {
    # 文本文件
    'txt', 'doc', 'docx', 'pdf',
    # 图片文件
    'jpg', 'jpeg', 'png', 'gif',
    # 视频文件
    'mp4', 'avi', 'mov', 'wmv'
}

# 数据库配置
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "interview_assistant")
}

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # 用于JWT token加密
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 