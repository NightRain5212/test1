import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
  // 加载当前模式下的环境变量
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': {
          //target: env.VITE_API_BASE_URL_TEST, // 使用加载的环境变量
          target:"http://127.0.0.1:8000",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api/'),
          secure: false,
        }
      }
    }
  };
});