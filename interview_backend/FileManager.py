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