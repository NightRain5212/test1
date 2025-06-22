import axios from 'axios';
import { message } from 'ant-design-vue';

// 根据环境变量切换基础URL
// const BASE_URL = import.meta.env.DEV //vite提供的环境变量，判断是否是开发环境
//   ? '/api' // 开发环境使用代理
//   : import.meta.env.VITE_API_BASE_URL_PROD; // 生产环境用真实URL
const BASE_URL = '/api'; // /api前面的路径都会被删除,用于绕过浏览器限制
const instance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 检查token是否过期
export function isTokenExpired(token) {
  try {
      // 解码 JWT 的 payload 部分,payload是一个对象
      const payload = JSON.parse(atob(token.split('.')[1])); 
      
      // 将 payload.exp (字符串时间) 转换为时间戳
      //创建Date对象支持格式为YYYY-MM-DD HH:mm:ss的字符串
      const expTimestamp = new Date(payload.exp).getTime(); // getTime()计算Date对象与1970-01-01 00:00:00的时间差，以毫秒为单位

      // 比较 expTimestamp 和 Date.now() 的毫秒数
      return expTimestamp < Date.now();//Date.now()是一个数值，以毫秒为单位。表示与1970-01-01 00:00:00的时间差
  } catch (error) {
      // 如果解析失败，视为令牌已过期
      return true;
  }
}

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    console.error('请求错误：', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  response => {
    const res = response.data;
    // 如果返回的状态码不是200，说明出错了
    if (res.code !== 200) {
      message.error(res.message || '请求失败');
      // 如果是401，说明token过期，需要重新登录
      if (res.code === 401) {
        // 清除token
        localStorage.removeItem('token');
        // 跳转到登录页
        window.location.href = '/login';
      }
      return Promise.reject(new Error(res.message || '请求失败'));
    }
    return res;
  },
  error => {
    console.error('响应错误：', error);
    // 处理网络错误
    if (!error.response) {
      message.error('网络错误，请检查您的网络连接');
    }
    // 处理HTTP错误
    else {
      const status = error.response.status;
      switch (status) {
        case 401:
          message.error('未授权，请重新登录');
          // 清除token
          localStorage.removeItem('token');
          // 跳转到登录页
          window.location.href = '/login';
          break;
        case 403:
          message.error('拒绝访问');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error('服务器错误');
          break;
        default:
          message.error(`请求失败：${error.message}`);
      }
    }
    return Promise.reject(error);
  }
);

export default instance;