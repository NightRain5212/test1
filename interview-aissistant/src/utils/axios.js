import axios from 'axios';

// 根据环境变量切换基础URL
// const BASE_URL = import.meta.env.DEV //vite提供的环境变量，判断是否是开发环境
//   ? '/api' // 开发环境使用代理
//   : import.meta.env.VITE_API_BASE_URL_PROD; // 生产环境用真实URL
const BASE_URL ='/api' // /api前面的路径都会被删除
const instance = axios.create({
  baseURL: BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error.response?.data || error);
  }
);

export default instance;