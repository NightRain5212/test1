from fastapi import FastAPI

# 创建实例化对象
app = FastAPI()

# 定义路径装饰器
# 请求路径:/  请求：get
@app.get("/")
# 路径操作函数，使用get访问/路径时被调用，异步函数节省时间
async def root() :
    return {"message":"hello world!"}