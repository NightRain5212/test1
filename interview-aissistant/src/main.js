import { createApp } from 'vue'
import App from './App.vue'
import Antd from 'ant-design-vue'
import { createPinia } from 'pinia'
import router from './router'//router是一个文件夹
import 'ant-design-vue/dist/reset.css' 
import naive from 'naive-ui'

const app = createApp(App)
const pinia = createPinia()

app.use(Antd) // 使用Ant Design Vue
app.use(naive)
app.use(router)
app.use(pinia); // 注册 Pinia状态管理
app.mount('#app')