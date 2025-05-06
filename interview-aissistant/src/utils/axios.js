import axios from 'axios';

// 根据环境变量切换基础URL
// const BASE_URL = import.meta.env.DEV //vite提供的环境变量，判断是否是开发环境
//   ? '/api' // 开发环境使用代理
//   : import.meta.env.VITE_API_BASE_URL_PROD; // 生产环境用真实URL
const BASE_URL ='/api' // /api前面的路径都会被删除,用于绕过浏览器限制
const instance = axios.create({
  baseURL: BASE_URL,
  timeout: 5000,
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
instance.interceptors.request.use(
  (config) => {
    try {
      // 从安全存储获取token（可根据环境替换为更安全的存储方式）
      const access_token = localStorage.getItem('accessToken');
      const refresh_token = localStorage.getItem('refreshToken');
      
      // 验证token格式有效性
      const isValidToken = (token) => {
        return token && typeof token === 'string' && token.trim().length > 0;
      };

      // 添加Authorization头
      if (isValidToken(access_token)) {
        config.headers.Authorization = `Bearer ${access_token.trim()}`;
      }

      // 添加RefreshToken头（根据后端需求决定是否发送）
      if (isValidToken(refresh_token)) {
        config.headers['X-Refresh-Token'] = refresh_token.trim(); // 建议使用X-前缀表示自定义头
      }

      return config;
    } catch (error) {
      console.error('请求拦截器处理失败:', error);
      return Promise.reject(new Error('请求配置处理失败'));
    }
  },
  (error) => {
    // 请求配置错误的统一处理
    console.error('请求拦截器配置错误:', error);
    return Promise.reject(error);
  }
);
//响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response.data;//直接返回响应tibody
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error.response?.data || error);
  }
);

export default instance;