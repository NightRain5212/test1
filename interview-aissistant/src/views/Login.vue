<template>
    <div class="main-all">
        <!-- 顶部导航栏 -->
        <header>
            <nav>
                <div class="links-box">
                </div>
                <div @click="change_display_loginform" class="nav-login-box">
                    LOGIN
                </div>
            </nav>
        </header>
        <!-- 登陆表单界面 -->
         <Transition name="fade">
        <div v-if="display_loginform" class="loginform-box">
            <form action="">
                <div class="input-box">
                    <label for="username">用户名:</label>
                    <input type="text" id="username" placeholder="请输入4-30位用户名" v-model=input_info.username>
                </div>

                <div class="input-box">
                    <label for="password">密码:</label>
                    <input type="password" id="password" placeholder="请输入8-12位密码" v-model=input_info.password>
                </div>

                <div class="login-btn-box">
                    <button class="login-btn" @click="login(input_info)">Login</button>
                </div>
            </form>
        </div>
         </Transition>
    </div>
</template>
<script setup>
import { ref } from 'vue';
//登录
import axios from "../utils/axios";
import { useRouter } from 'vue-router'
const route = useRouter() // 获取全局路由实例，一个app只有一个route实例
import{Modal,message} from "ant-design-vue";
const input_info = ref({
    username: '',
    password: '',
    email: ''
})
// 是否显示登陆界面
const display_loginform = ref(false)
// 更新登陆界面状态
const change_display_loginform = () => {
    display_loginform.value = !display_loginform.value;
}
// 登录函数（含JWT双令牌处理）
async function login(input_info) {
    if (input_info.username === '' || input_info.password === '') {
        message.info('用户名或密码不能为空');
        return ;
    }

    try {
        // 1. 验证用户是否存在
        const res = await axios.post('/api/user/get_info', {
            username: input_info.username
        });

        if (!res.data) {
            message.error('用户不存在');
            Modal.confirm({
                title: '用户未注册',
                content: '该用户未注册，是否立即注册？',
                okText: '是',
                cancelText: '否',
                onOk() {
                    register(); // 调用你的注册函数
                },
                onCancel() {
                    message.info('已取消注册');
                },
            });
            return;
        }

        // 2. 验证密码
        if (input_info.password !== res.data.password) {
            message.error('密码错误');
            return ;
        }

        // 3. 登录成功，获取双令牌
        const tokenRes = await axios.post('/api/auth/login', {
            username: input_info.username,
            password: input_info.password
        });

        // 4. 存储令牌
        localStorage.setItem('accessToken', tokenRes.data.accessToken);
        localStorage.setItem('refreshToken', tokenRes.data.refreshToken);

        // 5. 启动令牌自动刷新
        startTokenRefresh();
        message.success('欢迎回来！' + input_info.username);
        return ;

    } catch (error) {
        message.error('登录失败');
        return ;
    }
}

// accessToken令牌刷新函数
async function refreshTokens() {
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
        // 无有效refreshToken，跳转登录
        // window.location.href = '/login';
        route.push('/login');
        return;
    }

    try {
        // 1. 用refreshToken获取新accessToken
        //第二个参数是请求体,第三个参数是配置，这里设置请求头
        const res = await axios.post('/api/auth/refresh', null, {
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });

        // 2. 更新本地令牌
        localStorage.setItem('accessToken', res.data.accessToken);

        // 3. 重新发起之前的请求（如果有）
        if (res.data.refreshToken) {
            localStorage.setItem('refreshToken', res.data.refreshToken);
        }

    } catch (error) {
        if (error.response?.status === 401) { // 可选链操作符避免报错,等价于error.response && error.response.status === 401
            localStorage.clear();
            route.push('/login');
        } else {
            console.error('非HTTP错误:', error.message);
        }
    }
}

// 启动定时令牌刷新
let refreshInterval;
function startTokenRefresh() {
    // 清除旧定时器
    if (refreshInterval) clearInterval(refreshInterval);

    // 每5分钟检查一次（根据实际token有效期调整）,setInterval是内置函数，接收两个参数，第一个是要执行的函数，第二个是执行时间间隔
    refreshInterval = setInterval(async () => {
        const accessToken = localStorage.getItem('accessToken');

        // 如果accessToken不存在或已过期
        if (!accessToken || isTokenExpired(accessToken)) {
            await refreshTokens();
        }
    }, 5 * 60 * 1000); // 5分钟
}

// 检查token是否过期
function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));//jwt令牌分为三个部分,header,paylod(存放实际数据),signature(加密)
        return payload.exp * 1000 < Date.now();//payload.exp实际上是截止时间，以毫秒为单位
    } catch {
        return true;
    }
}
async function register(input_info) {
    try {
        const res = await axios.post('/api/auth/register', {
            ...input_info
        })

        // 2. 存储令牌
        localStorage.setItem('accessToken', res.data.accessToken);
        localStorage.setItem('refreshToken', res.data.refreshToken);

        // 3. 启动令牌自动刷新
        startTokenRefresh();
        message.success('欢迎！' + input_info.username);
        return;
    } catch (error) {
        message.error('注册失败');
    }
}
</script>
<style scoped lang="scss">
.main-all {
    height: 100vh;
    width: 100%;
    padding: 0px;
    margin: 0px;
    position: relative; //相对定位
    background: linear-gradient(to right,
            rgba(235, 65, 139, 0.833),
            rgba(151, 40, 236, 0.84));
}

header {
    background: transparent;
    position: absolute;
    top: 0;
    height: 10%;
    width: 100%;

    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 100%;
        width: 100%;
        background: rgba(255, 254, 254, 0.336);
        user-select: none;
    }
}
/* 电视机打开效果 - 从中心向四周展开 */
/*transition的name自动匹配以name为前缀 */
.fade-enter-active, .fade-leave-active {
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55); /* 弹性动画 */
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;/* 透明度 */
  clip-path: circle(0% at 50% 50%); /* 从中心点收缩为 0 */
  transform: scale(0.8); /* 初始缩小 */
}

.fade-enter-to, .fade-leave-from {
  opacity: 1;/* 透明度 */
  clip-path: circle(100% at 50% 50%); /* 展开至全屏 */
  transform: scale(1); /* 恢复原大小 */
}

.links-box {
    background: transparent;
    width: 80%;
    height: 100%;
}

.nav-login-box {
    display: flex;
    background: transparent;
    width: 20%;
    height: 100%;
    font-size: 30px;
    align-items: center;
    justify-content: center;
    color: #fff;

    &:hover {
        /*&表示父元素*/
        cursor: pointer;
    }
}

.loginform-box {
    position: absolute;
    padding: 20px;
    top: 50%;
    left: 50%;
    width: 400px;
    height: 300px;
    transform: translate(-50%, -50%);
    background: #fff;
    display: flex;
    flex-direction: column;
    border-radius: 15px;
}

.input-box {
    display: flex;
    background: transparent;
    text-align: center;
    margin: 10px auto;
    height: 80px;
    justify-content: space-between;
    align-items: center;

    input {
        height: 30px;
        width: 80%;
        outline: none;
        border: solid 2px skyblue;
        border-radius: 5px;
        padding-left: 20px;
    }

    .login-title h2 {
        font-size: 100px;
    }
}

.login-btn-box {
    background: transparent;
    height: 80px;
    text-align: center;
    display: flex;
    justify-content: space-around;
    align-items: center;
    cursor: pointer;

    .login-btn {
        height: 50%;
        width: 150px;
        border: none;
        border-radius: 5px;
        font-size: 25px;
        background: transparent;
    }

    a {
        text-decoration: none;
        font-size: 15px;
    }
}
</style>
