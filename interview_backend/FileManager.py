import oss2
from oss2 import Bucket, Auth
from typing import Optional
import urllib.parse#用于url编码
import os
import tempfile#用于创建临时目录,供前端下载文件
import zipfile#用于压缩文件
from fastapi import HTTPException
from fastapi.responses import FileResponse
from typing import List
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from datetime import datetime

class FileManager:
    def __init__(self, access_key_id: str, access_key_secret: str, bucket_name: str, endpoint: str):
        """
        初始化OSS文件管理器
        :param access_key_id: OSS访问ID
        :param access_key_secret: OSS访问密钥
        :param bucket_name: 存储桶名称
        :param endpoint: OSS端点地址 (如: https://oss-cn-hangzhou.aliyuncs.com)
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.bucket_name = bucket_name
        self.endpoint = endpoint.rstrip('/')  # 去除末尾斜杠
        self.bucket: Optional[Bucket] = None
        self.UPLOAD_DIR = Path("uploads")
        self.ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'mp4', 'webm', 'mp3', 'wav'}
        
        # 确保上传目录存在
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (self.UPLOAD_DIR / "resumes").mkdir(exist_ok=True)
        (self.UPLOAD_DIR / "videos").mkdir(exist_ok=True)
        (self.UPLOAD_DIR / "audios").mkdir(exist_ok=True)
        (self.UPLOAD_DIR / "reports").mkdir(exist_ok=True)

    def connect(self) -> Bucket:
        """
        连接OSS并返回Bucket对象
        :return: OSS Bucket实例
        """
        try:
            if not self.bucket:
                auth = Auth(self.access_key_id, self.access_key_secret)
                self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
                print(f"已连接到OSS: {self.bucket_name}")
        except Exception as e:
            print(f"连接OSS失败: {e}")
            return
        return self.bucket

    def upload_file(self, file_obj, file_path: str) -> str:
        """
        上传文件到OSS
        :param file_obj: 文件对象
        :param file_path: 文件在OSS中的路径
        :return: 文件URL
        """
        #阿里云url地址格式:
        #https://{bucket-name}.{region}.aliyuncs.com/{object-name}
        #https://{region}.aliyuncs.com/{bucket-name}/{object-name}

        bucket = self.connect()
        result = bucket.put_object(file_path, file_obj)

        # 确保endpoint是规范化的域名（不含协议和路径）
        endpoint = self.endpoint.replace('https://', '').replace('http://', '').split('/')[0]

        if result.status == 200:
            # 使用三级域名格式
            return f"https://{self.bucket_name}.{endpoint}/{file_path}"
        raise Exception(f"上传文件失败: {result.status}")

    def delete_file(self, file_path: str) -> bool:
        """
        删除OSS文件
        :param file_path: 文件在OSS中的路径
        :return: 是否删除成功
        """
        bucket = self.connect()
        result = bucket.delete_object(file_path)
        return result.status == 204

    def get_file_url(self, file_path: str) -> str:
        """
        获取文件完整URL
        :param file_path: 文件在OSS中的路径
        :return: 完整的访问URL
        """
        # 对文件路径进行URL编码
        encoded_path = urllib.parse.quote(file_path)
        return f"https://{self.bucket_name}.{self.endpoint.replace('https://', '').replace('http://', '')}/{encoded_path}"

    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        :param file_path: 文件在OSS中的路径
        :return: 是否存在
        """
        bucket = self.connect()
        return bucket.object_exists(file_path)

    def list_files(self, prefix: str = '', delimiter: str = '') -> list:
        """
        列出文件
        :param prefix: 前缀
        :param delimiter: 分隔符
        :return: 文件列表
        """
        bucket = self.connect()
        objects = oss2.ObjectIterator(bucket, prefix=prefix, delimiter=delimiter)
        return [obj.key for obj in objects]

    def download_files(self, urls: List[str], max_files: int = 10) -> str:
        """
        批量下载OSS文件到本地临时目录并打包为zip
        :param urls: 文件URL列表
        :param max_files: 最大允许下载数量
        :return: 临时zip文件路径
        """
        if len(urls) > max_files:
            raise ValueError(f"一次最多下载{max_files}个文件")

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "download.zip")

        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for index, url in enumerate(urls):
                    try:
                        # 从URL中提取object key
                        object_key = self._extract_object_key(url)
                        if not object_key:
                            continue
                        # 下载文件到临时目录给前端下载,保证顺序
                        temp_file = os.path.join(temp_dir, f"{index}_{os.path.basename(object_key)}")

                        # 下载并添加到ZIP（保持原始顺序）
                        self._download_single_file(object_key, temp_file)
                        zipf.write(temp_file, arcname=f"{index}_{os.path.basename(object_key)}")

                        os.remove(temp_file)  # 删除临时文件

                    except Exception as e:
                        print(f"下载文件 {url} 失败: {str(e)}")
                        continue

            return zip_path

        except Exception as e:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail=f"创建下载包失败: {str(e)}")

    def _extract_object_key(self, url: str) -> Optional[str]:
        """从OSS URL中提取object key"""
        base_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/"
        if url.startswith(base_url):
            return url[len(base_url):]
        return None

    def _download_single_file(self, object_key: str, save_path: str):
        """下载单个文件到本地"""
        bucket = self.connect()
        bucket.get_object_to_file(object_key, save_path)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def save_file(self, file: UploadFile, category: str) -> str:
        """保存上传的文件到指定目录"""
        try:
            # 生成唯一文件名
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            
            # 确定保存路径
            save_dir = self.UPLOAD_DIR / category
            save_dir.mkdir(exist_ok=True)
            file_path = save_dir / filename
            
            # 保存文件
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            return str(file_path)
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            raise

    async def extract_resume_content(self, file_path: str) -> str:
        """从不同格式的简历文件中提取文本内容"""
        try:
            file_path = Path(file_path)
            ext = file_path.suffix.lower()
            
            if ext == '.txt':
                # 文本文件直接读取
                return file_path.read_text(encoding='utf-8')
            
            elif ext == '.pdf':
                # PDF文件
                content = []
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        content.append(page.extract_text())
                return '\n'.join(content)
            
            elif ext in ['.doc', '.docx']:
                # Word文档
                doc = Document(file_path)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            elif ext in ['.png', '.jpg', '.jpeg']:
                # 图片文件，使用OCR
                image = Image.open(file_path)
                return pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            else:
                raise ValueError(f"不支持的文件类型: {ext}")
                
        except Exception as e:
            print(f"提取简历内容失败: {str(e)}")
            raise

    async def generate_report(self, report_data: dict, output_path: str) -> str:
        """生成面试报告PDF文件"""
        try:
            # 注册中文字体
            pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
            
            # 创建PDF文件
            c = canvas.Canvas(output_path, pagesize=letter)
            c.setFont('SimSun', 16)
            
            # 标题
            c.drawString(100, 750, "面试评估报告")
            c.setFont('SimSun', 12)
            
            # 基本信息
            c.drawString(100, 700, f"面试ID: {report_data['interview_id']}")
            c.drawString(100, 680, f"总分: {report_data['total_score']:.1f}")
            c.drawString(100, 660, f"评级: {report_data['rating']}")
            c.drawString(100, 640, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 问题和答案评估
            y = 600
            for i, question in enumerate(report_data['questions'], 1):
                if y < 100:  # 如果页面空间不足，添加新页面
                    c.showPage()
                    c.setFont('SimSun', 12)
                    y = 750
                
                c.drawString(100, y, f"问题 {i}: {question['question']}")
                y -= 20
                c.drawString(120, y, f"答案: {question.get('answer_text', '未作答')}")
                y -= 20
                c.drawString(120, y, f"得分: {question.get('score', 0):.1f}")
                y -= 30
            
            # 简历分析
            if y < 200:  # 如果页面空间不足，添加新页面
                c.showPage()
                c.setFont('SimSun', 12)
                y = 750
            
            c.drawString(100, y, "简历分析:")
            y -= 20
            resume_content = report_data['resume_analysis']['content']
            # 简单的文本换行处理
            words = resume_content.split()
            line = ""
            for word in words:
                if len(line + word) < 50:  # 假设每行50个字符
                    line += word + " "
                else:
                    c.drawString(120, y, line)
                    y -= 20
                    line = word + " "
            if line:
                c.drawString(120, y, line)
            
            # 保存PDF
            c.save()
            return output_path
            
        except Exception as e:
            print(f"生成报告失败: {str(e)}")
            raise