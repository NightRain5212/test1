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
        <div v-if="display_loginform" class="loginform-box">
            <form action="">
                <div class="login-title">
                    <h2>Login</h2>
                </div>

                <div class="input-box">
                    <label for="username">用户名:</label>
                    <input type="text" id="username">
                </div>

                <div class="input-box">
                    <label for="password">密码:</label>
                    <input type="password" id="password">
                </div>

                <div class="login-btn-box">
                    <button class="login-btn">Login</button>
                    <p><a href="#">To Sign up</a></p>
                </div>
            </form>
        </div>
    </div>
</template>
<script setup>
//登录
import { ref } from 'vue';
import axios from "../utils/axios";

// 是否显示登陆界面
const display_loginform = ref(false)

// 更新登陆界面状态
const change_display_loginform = () => {
    display_loginform.value = !display_loginform.value;
}
// 登录函数（含JWT双令牌处理）
async function login(input_info) {
    if (input_info.username === '' || input_info.password === '') {
        return { message: '用户名或密码不能为空', code: 0 };
    }

    try {
        // 1. 验证用户是否存在
        const res = await axios.post('/api/user/get_info', { 
            username: input_info.username 
        });

        if (!res.data) {
            hint('该用户不存在，是否注册？');
            return { message: '该用户未注册', code: 404 };
        }

        // 2. 验证密码
        if (input_info.password !== res.data.password) {
            return { message: '密码错误', code: 401 };
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

        return { 
            message: '欢迎回来！' + input_info.username, 
            ...res.data,
            code: 200 
        };

    } catch (error) {
        console.error('登录失败:', error);
        return { 
            message: '登录服务异常', 
            code: 500 
        };
    }
}

// 令牌刷新函数（优化版）
async function refreshTokens() {
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (!refreshToken) {
        // 无有效refreshToken，跳转登录
        window.location.href = '/login';
        return;
    }

    try {
        // 1. 用refreshToken获取新accessToken
        const res = await axios.post('/api/auth/refresh', null, {
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });

        // 2. 更新本地令牌
        localStorage.setItem('accessToken', res.data.accessToken);
        
        // 如果有新refreshToken也更新（可选）
        if (res.data.refreshToken) {
            localStorage.setItem('refreshToken', res.data.refreshToken);
        }

    } catch (error) {
        if (error.response?.status === 401) {
            // refreshToken已过期，强制重新登录
            localStorage.clear();
            window.location.href = '/login';
        }
    }
}

// 启动定时令牌刷新
let refreshInterval;
function startTokenRefresh() {
    // 清除旧定时器
    if (refreshInterval) clearInterval(refreshInterval);
    
    // 每5分钟检查一次（根据实际token有效期调整）
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
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
    } catch {
        return true;
    }
}

</script>
<style scoped lang="scss">
.main-all {
    height: 100vh;
    width: 100%;
    padding:0px;
    margin:0px;
    position: relative;//相对定位
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
    width: 30%;
    height: 380px;
    transform: translate(-50%, -50%);
    background: #fff;
    display: flex;
    flex-direction: column;
    border-radius: 15px;
}

.loginform-box .login-title {
    margin-top: 0px;
    background: transparent;
    text-align: center;
    margin-bottom: 10px;
    height: 70px;
    line-height: 70px;
    font-size: large;
    font-weight: bolder;
}

.input-box {
    display: flex;
    background: transparent;
    text-align: center;
    margin: 10px auto;
    height: 80px;
    justify-content: space-between;
    align-items: center;
}

.input-box input {
    height: 30px;
    width: 80%;
    outline: none;
    border: solid 2px skyblue;
    border-radius: 5px;
    padding-left: 20px;
}

.input-box .login-title h2 {
    font-size: 100px;
}

.login-btn-box {
    background: transparent;
    height: 80px;
    text-align: center;
    display: flex;
    justify-content: space-around;
    align-items: center;
}

.login-btn-box .login-btn {
    height: 50%;
    width: 150px;
    border: none;
    border-radius: 5px;
    font-size: 25px;
    background: transparent;
}

.login-btn-box a {
    text-decoration: none;
    font-size: 15px;
}
</style>
