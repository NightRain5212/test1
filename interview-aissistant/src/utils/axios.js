import axios from 'axios';
const BASE_URL = import.meta.env.VITE_API_BASE_URL_TEST
//const BASE_URL = import.meta.env.VITE_API_BASE_URL_PROD

// 创建 axios 实例
const instance = axios.create({
    baseURL: BASE_URL, // API 基础路径
    timeout: 5000, // 请求超时时间
    headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器,现在还没什么用
instance.interceptors.request.use(
  (config) => {//config是请求的配置
    // 在发送请求之前处理
    const token = localStorage.getItem('token');//localStorage是浏览器提供的本地存储机制，存职机制类似map
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }//如果浏览器本地存储的有token，那么就需要添加在请求报文中，以便通讯验证
    return config;
  },
  (error) => {
    // 请求错误处理
    return Promise.reject(error);//promise是js提供的异步编程的解决方案，本身是一个对象
  }
);

// 响应拦截器，现在还没什么用
instance.interceptors.response.use(
  (response) => {//response是客户端收到的响应报文
    // 对响应数据进行处理
    //没做处理，直接返回(通过)
    return response.data;
  },
  (error) => {
    // 响应错误处理
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
export default instance;
