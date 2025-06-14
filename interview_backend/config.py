import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent
#STORAGE_DIR = Path("D:/interview_storage")  # 文件存储根目录
STORAGE_DIR = BASE_DIR / "interview_storage"  # 文件存储根目录
# 创建存储目录结构
UPLOAD_DIR = STORAGE_DIR / "uploads"  # 上传文件目录
TEMP_DIR = STORAGE_DIR / "temp"      # 临时文件目录
VIDEO_DIR = STORAGE_DIR / "videos"   # 视频文件目录
AUDIO_DIR = STORAGE_DIR / "audio"    # 音频文件目录

# 确保所有必要的目录都存在
for directory in [UPLOAD_DIR, TEMP_DIR, VIDEO_DIR, AUDIO_DIR,STORAGE_DIR]:
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

# 讯飞星火大模型配置
SPARK_CONFIG = {
    "app_id": os.getenv("SPARK_APP_ID", ""),
    "api_key": os.getenv("SPARK_API_KEY", ""),
    "api_secret": os.getenv("SPARK_API_SECRET", ""),
    "spark_url": "wss://spark-api.xf-yun.com/v3.1/chat",  # v3.1版本的API地址
    "domain": "generalv3",  # 使用V3版本的通用大模型
} 