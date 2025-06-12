import oss2
from oss2 import Bucket, Auth
from typing import Optional
import urllib.parse#用于url编码
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