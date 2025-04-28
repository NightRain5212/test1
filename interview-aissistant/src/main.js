import { createApp } from 'vue'
import App from './App.vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css' // 引入ant-design-vue的全局样式

const app = createApp(App)
app.use(Antd) // 使用Ant Design Vue
app.mount('#app')