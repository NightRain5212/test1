import asyncio
from spark_client import SparkClient

async def test_connection():
    client = SparkClient()
    try:
        # 创建WebSocket连接
        ws_url = client._create_url()
        print(f"生成的URL: {ws_url}")
        
        # 测试一个简单的对话
        response = await client.chat("你好")
        print(f"响应: {response}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 