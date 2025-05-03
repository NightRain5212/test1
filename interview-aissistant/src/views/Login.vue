<template>
    <div class="main-all">
        <!-- 顶部导航栏 -->
        <header>
            <nav>
                <div class="links-box">
                </div>
                <div @click="openloginform" class="nav-login-box">
                    LOGIN
                </div>
            </nav>
        </header>
        <!-- 登陆表单界面 -->
        <Transition name="fade">
            <!-- 阻止表单默认行为 -->
            <div v-show="display_loginform" class="loginform-box " @submit.prevent="login(input_info)">
                <!-- 退出按钮 -->
                <button class="close-btn" @click="closeLoginForm">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                        :stroke="hoverClose ? '#fff' : '#999'" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
                <form  autocomplete="off">
                    <div class="input-box">
                        <label for="username">用户名:</label>
                        <input type="text" id="username" placeholder="请输入4-30位用户名" v-model="input_info.username"
                            required minlength="4" maxlength="30">
                    </div>

                    <div class="input-box">
                        <label for="password">密码:</label>
                        <input type="password" id="password" placeholder="请输入8-12位密码" v-model="input_info.password"
                            required minlength="8" maxlength="12">
                    </div>

                    <div class="login-submit-btn">
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
import { debounce } from 'lodash-es';// 防抖函数
const input_info = ref({
    username: '',
    password: '',
    email: ''
})
// 是否显示登陆界面
const display_loginform = ref(false)
// 更新登陆界面状态
const openloginform = () => {
    display_loginform.value = true;
}
function closeLoginForm (){
    display_loginform.value = false; 
    input_info.value = {username: '',password: '',email: ''}
}
// 正则表达式定义
/**
 * - username 4~30 位,字母、汉字、数字、连字符（-），不能以数字开头，不能包含空格
 *  password 8~12 位 字母、数字、特殊字符（!@#$%^&*()_+）,至少包含字母和数字，不能包含空格和汉字
-* email 最长50个字符，也可以没有
 */
const usernameRegex = /^[a-zA-Z\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5-]{3,29}$/;
const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[!-~]{8,12}$/;
// 真正的登录逻辑（不含防抖）
async function performLogin(input_info) {

    const hideLoading = message.loading('登录中...', 0);//0表示需要手动调用hideLoading函数关闭
    
    try {
        // 1. 验证用户是否存在
        const res = await axios.post('/api/user/get_info', {
            username: input_info.username
        });

        if (!res?.data) {
            message.error('用户不存在');
            Modal.confirm({
                title: '用户未注册',
                content: '该用户未注册，是否立即注册？',
                okText: '是',
                cancelText: '否',
                onOk: register, // 直接引用注册函数
                onCancel: () => message.info('已取消注册'),
            });
            return false;
        }

        // 2. 验证密码
        if (input_info.password !== res.data.password) {
            message.error('密码错误');
            return false;
        }

        // 3. 获取双令牌
        const tokenRes = await axios.post('/api/auth/login', input_info);
        if (!tokenRes?.data) {
            message.error('登录失败');
            return false;
        }

        // 4. 存储令牌
        localStorage.setItem('accessToken', tokenRes.data.accessToken);
        localStorage.setItem('refreshToken', tokenRes.data.refreshToken);

        // 5. 启动令牌刷新
        startTokenRefresh();
        message.success(`欢迎回来！${input_info.username}`);
        return true;
    } catch (error) {
        message.error(error.response?.data?.message || '登录失败');
        return false;
    } finally {
        hideLoading();
    }
}

// 防抖只防抖网络请求部分,提升用户体验
const debouncedLogin = debounce(async (input_info, resolve) => {
    const result = await performLogin(input_info);
    resolve(result);
}, 1000, { leading: true, trailing: false });//配置：连续点击中，第一次立即执行，最后一次不会执行,其他都延迟间隔

// 对外暴露的登录函数
async function login(input_info) {
    //这里promise传入一个函数,这个函数被传入一个js提供的resolve函数
    return new Promise((resolve) => {
        // 立即执行验证逻辑
        if (input_info.username === '' || input_info.password === '') {
            message.info('用户名或密码不能为空');
            return resolve(false);
        }
        
        if (!usernameRegex.test(input_info.username)) {
            message.error('用户名必须为4-30位字母/汉字/数字/连字符组合，且不能以数字开头');
            return resolve(false);
        }
        
        if (!passwordRegex.test(input_info.password)) {
            message.error('密码必须为8-12位，包含字母和数字，可加特殊字符(!@#$%^&*等)');
            return resolve(false);
        }
        
        // 防抖执行网络请求,接着把resolve函数传给debouncedLogin
        debouncedLogin(input_info, resolve);
    });
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
        if (res.data?.refreshToken) {
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
//注册了之后要重新登录
async function register(input_info) {
    try {
        const res = await axios.post('/api/auth/register', {
            ...input_info
        })
        if (!res?.data) {
            message.error('注册失败');
            return;
        }
        message.success('注册成功！请登录！');
        display_loginform.value=true;
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

.close-btn {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 32px;
    height: 32px;
    border-radius: 4px;//圆角
    display: flex;
    align-items: center;//垂直居中
    justify-content: center;//水平居中
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
    z-index: 1000;

    &:hover {
        background: #ff4444;
    }

    &:active {
        transform: scale(0.9);//大小最终缩小到0.9倍
        transition: transform 0.1s ease; //0.1秒内缩小
    }

    svg {
        transition: stroke 0.2s ease; 
    }
}
.input-box {
    position:relative;
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
        outline: none;//去除输入框的轮廓线
        border: solid 2px skyblue;
        border-radius: 5px;
        padding-left: 20px;
    }

    .login-title h2 {
        font-size: 100px;
    }
}

.login-submit-btn {
    background: transparent;
    height: 80px;
    text-align: center;
    display: flex;
    justify-content: space-around;
    align-items: center;
    transition: all 0.3s ease;
    /* 添加过渡效果 */

    .login-btn {
        height: 50%;
        width: 80px;
        border: none;
        border-radius: 5px;
        font-size: 25px;
        background: transparent;
        transition: all 0.3s ease;/* 按钮单独过渡 */
        position: relative;/* 为动画效果做准备 */
        color: #333;/* 默认文字颜色 */
        cursor: pointer; /* 鼠标指针样式 */
        overflow: hidden;/* 防止内容溢出 */
        
        /* 鼠标悬浮效果 */
        &:hover {
            color: #1a73e8;
            /* 悬浮时文字颜色变化 */
            transform: translateY(-3px);
            /* 上浮效果 */
            text-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            /* 添加轻微阴影增强立体感 */
        }

        /* 按钮按下效果 */
        &:active {
            transform: translateY(1px);
            /* 下压效果 */
            text-shadow: none;
            /* 移除阴影 */
            color: #0d5bba;
            /* 按下时颜色更深 */
        }
    }
}
</style>
