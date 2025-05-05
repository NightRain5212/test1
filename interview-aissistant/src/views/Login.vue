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
            <div v-if="display_loginform" class="loginform-box" @submit.prevent="login(input_info)" moUseleave="hoverClose = false" 
                mouseenter="hoverClose = true">
                <!-- 退出按钮 -->
                <button class="close-btn" @click="closeLoginForm">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                        :stroke="hoverClose ? '#fff' : '#999'" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
                <Transition name="form-switch" mode="out-in">

                <!-- 登录表单 -->
                <form  autocomplete="off" v-if="!isRegisterMode">
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
                    <div class="switch-mode">
                        <span>还没有账号？</span>
                        <a href="#" @click.prevent="switchMode">立即注册</a>
                    </div>
                </form>

                <!-- 注册表单 -->
                <form autocomplete="off" v-else @submit.prevent="handleRegister">
                    <div class="input-box">
                        <label for="reg-username">用户名:</label>
                        <input type="text" id="reg-username" 
                            placeholder="请输入4-30位用户名" 
                            v-model="register_info.username"
                            required minlength="4" maxlength="30">
                    </div>

                    <div class="input-box">
                        <label for="reg-email">邮箱:</label>
                        <input type="email" id="reg-email" 
                            placeholder="请输入邮箱" 
                            v-model="register_info.email"
                            required>
                    </div>

                    <div class="input-box">
                        <label for="reg-password">密码:</label>
                        <input type="password" id="reg-password" 
                            placeholder="请输入8-12位密码" 
                            v-model="register_info.password"
                            required minlength="8" maxlength="12">
                    </div>

                    <div class="input-box">
                        <label for="reg-confirm">确认密码:</label>
                        <input type="password" id="reg-confirm" 
                            placeholder="请再次输入密码" 
                            v-model="register_info.confirmPassword"
                            required>
                    </div>

                    <div class="login-submit-btn">
                        <button class="login-btn" @click="handleRegister">注册</button>
                    </div>

                    <div class="switch-mode">
                        <span>已有账号？</span>
                        <a href="#" @click.prevent="switchMode">返回登录</a>
                    </div>
                </form>
                </Transition>
            </div>
        </Transition>

    </div>
</template>
<script setup>
import { h, ref } from 'vue';
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
// 注册表单数据
const register_info = ref({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
});
const hoverClose = ref(false)//一个退出按钮的变量
// 是否显示登陆界面
const display_loginform = ref(false)
// 更新登陆界面状态
const openloginform = () => {
    display_loginform.value = true;
     input_info.value = {username: '',password: '',email: ''}
    isRegisterMode.value = false;
}
function closeLoginForm (){
    display_loginform.value = false; 
    input_info.value = {username: '',password: '',email: ''}
    // 延迟重置表单高度
    setTimeout(() => {
        const formBox = document.querySelector('.loginform-box');
        if (formBox) {
            formBox.style.height = '300px';
        }
    }, 300);

}
// 正则表达式定义
/**
 * - username 4~30 位,字母、汉字、数字、连字符（-），不能以数字开头，不能包含空格
 *  password 8~12 位 字母、数字、特殊字符（!@#$%^&*()_+）,至少包含字母和数字，不能包含空格和汉字
-* email 最长50个字符，也可以没有
 */
 const usernameRegex = /^[a-zA-Z\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5-]{3,29}$/;
const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[!-~]{8,12}$/;

async function performLogin(input_info) {
    const hideLoading = message.loading('登录中...', 0);

    try {
        // 1. 验证用户是否存在
        const res = await axios.get('/user/get_info', {
            params: {
                username: input_info.username
            }
        });

        // 用户不存在时的处理
        if (!res?.data) {
            return await handleUserNotExist(input_info);
        }

        // 2. 密码验证
        if (!res.data?.password || input_info.password !== res.data.password) {
            message.error(userData?.password ? '密码错误' : '无效密码');
            return false;
        }

        // 3. 登录流程
        return await handleLoginSuccess(input_info);
    } catch (error) {
        handleLoginError(error);
        return false;
    } finally {
        hideLoading();
    }
}

// 用户不存在处理
async function handleUserNotExist(input_info) {
    message.error('用户不存在f55');
    
    return new Promise((resolve) => {
        Modal.confirm({
            title: '用户未注册',
            content: `用户"${input_info.username}"未注册，是否立即注册？`,
            okText: '注册',
            cancelText: '取消',
            async onOk() {
                try {
                    await register(input_info);
                    message.success('注册成功！请重新登录');
                    resolve('registered'); // 特殊返回值表示注册成功
                } catch (error) {
                    message.error(`注册失败: ${error.response?.data?.message || error.message}`);
                    resolve(false);
                }
            },
            onCancel() {
                message.info('已取消注册');
                resolve(false);
            }
        });
    });
}

// 登录成功处理
async function handleLoginSuccess(input_info) {
    try {
        const tokenRes = await axios.post('/auth/login', input_info);
        
        if (!tokenRes?.data?.accessToken) {
            message.error('登录失败: 令牌获取异常');
            return false;
        }

        // 存储令牌
        localStorage.setItem('accessToken', tokenRes.data.accessToken);
        localStorage.setItem('refreshToken', tokenRes.data.refreshToken);

        startTokenRefresh();
        message.success(`欢迎回来，${input_info.username}!`);
        return true;
    } catch (error) {
        handleLoginError(error);
        return false;
    }
}

// 错误处理
function handleLoginError(error) {
    const errorMessage = error.response?.data?.message || '登录失败';
    if (error.response?.status === 401) {
        message.error('认证失败: ' + errorMessage);
    } else {
        message.error('登录错误: ' + errorMessage);
    }
}

// 防抖登录
const debouncedLogin = debounce(async (input_info, resolve) => {
    const result = await performLogin(input_info);
    resolve(result);
}, 1000, { leading: true, trailing: false });//多次点击，第一次无间隔，最后一次无效

// 防抖注册
const debouncedRegister = debounce(async (register_info, resolve) => {
    const result = await register(register_info);
    resolve(result);
}, 1000, { leading: true, trailing: false });//多次点击，第一次无间隔，最后一次无效

// 对外暴露的登录函数
async function login(input_info) {
    // 输入验证
    function validateInput(input_info) {
        if (!input_info.username || !input_info.password) {
            message.info('用户名或密码不能为空');
            return false;
        }

        if (!usernameRegex.test(input_info.username)) {
            message.error('用户名必须为4-30位字母/汉字/数字/连字符组合，且不能以数字开头');
            return false;
        }

        if (!passwordRegex.test(input_info.password)) {
            message.error('密码必须为8-12位，包含字母和数字，可加特殊字符(!@#$%^&*等)');
            return false;
        }
        return true;
    }
    //resolve
    return new Promise((resolve) => {
        if (!validateInput(input_info)) {
            return resolve(false);
        }
        debouncedLogin(input_info, resolve);
    });
}

// 注册函数
async function register(register_info) {
    // try {
    //     const res = await axios.post('/auth/register', input_info);
        
    //     if (!res?.data) {
    //         throw new Error('注册响应数据为空');
    //     }
        
    //     return res.data;
    // } catch (error) {
    //     console.error('注册失败:', error);
    //     throw error; // 抛出错误让上层处理
    //}
    try {
        const res = await axios.post('/auth/register', {
            username: register_info.value.username,
            password: register_info.value.password,
            email: register_info.value.email
        })

        if (res.data) {
            message.success('注册成功！')
            // 切换到登录模式
            isRegisterMode.value = false
            // 预填充用户名
            input_info.value.username = register_info.value.username
        }
    } catch (error) {
        message.error(`注册失败: ${error.response?.data?.message || error.message}`);
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
        const res = await axios.post('/auth/refresh', null, {
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

// 控制表单模式
const isRegisterMode = ref(false)


// 邮箱验证正则
const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/

// 注册处理函数
async function handleRegister(e) {
    e.preventDefault(); // 阻止默认提交行为
    console.log('注册信息:', register_info.value)
    // 输入验证
    function validateInput(register_info) {

        if (!usernameRegex.test(register_info.value.username)) {
            message.error('用户名必须为4-30位字母/汉字/数字/连字符组合，且不能以数字开头');
            return false;
        }

        if (!passwordRegex.test(register_info.value.password)) {
            message.error('密码必须为8-12位，包含字母和数字，可加特殊字符(!@#$%^&*等)');
            return false;
        }

        if (register_info.value.password !== register_info.value.confirmPassword) {
            message.error('两次输入的密码不一致')
            return false;
        }
        if (!register_info.value.username || !register_info.value.password || 
            !register_info.value.email || !register_info.value.confirmPassword) {
            message.error('请填写所有必填项')
            return false;
        }
        if (!emailRegex.test(register_info.value.email)) {
            message.error('邮箱格式不正确')
            return false;
        }
        return true;
    }
    
    //resolve
    return new Promise((resolve) => {
        if (!validateInput(register_info)) {
            return resolve(false);
        }
        debouncedRegister(register_info, resolve);
    });


    try {
        const res = await axios.post('/auth/register', {
            username: register_info.value.username,
            password: register_info.value.password,
            email: register_info.value.email
        })

        if (res.data) {
            message.success('注册成功！')
            // 切换到登录模式
            isRegisterMode.value = false
            // 预填充用户名
            input_info.value.username = register_info.value.username
        }
    } catch (error) {
        message.error(`注册失败: ${error.response?.data?.message || error.message}`)
    }
}

// 切换登录/注册模式
function switchMode() {
    // 获取表单容器
    const formBox = document.querySelector('.loginform-box');
    
    // 切换前记录当前高度
    const startHeight = formBox.offsetHeight;
    
    // 切换表单模式
    isRegisterMode.value = !isRegisterMode.value;
    
    // 清空表单
    if (isRegisterMode.value) {
        register_info.value = {
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
        }
        // 设置注册表单高度
        formBox.style.height = '450px';
    } else {
        input_info.value = {
            username: '',
            password: ''
        }
        // 设置登录表单高度
        formBox.style.height = '300px';
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
/* 修复动画类名和效果 */
.fade-enter-active,
.fade-leave-active {
    transition: all 0.5s ease;
    will-change: transform, opacity;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.9);
}

.fade-enter-to,
.fade-leave-from {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
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
    position: fixed; // 改为 fixed 定位
    padding: 20px;
    top: 50%;
    left: 50%;
    width: 400px;
    transform: translate(-50%, -50%);
    background: #fff;
    display: flex;
    flex-direction: column;
    border-radius: 15px;
    height: auto;
    min-height: 300px;
    max-height: 500px;
    transition: all 0.3s ease;
    overflow: hidden;
    transform-origin: center center; // 添加变换原点
    will-change: transform, opacity; // 优化动画性能
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
    margin: 5px auto;
    height: 70px;
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
    label {
        min-width: 80px; // 固定标签宽度
        text-align: right;
        margin-right: 10px;
        color: #333;
    }
    
    input {
        // ...existing code...
        transition: border-color 0.3s ease;
        
        &:focus {
            border-color: #1a73e8;
            box-shadow: 0 0 0 2px rgba(26,115,232,0.2);
        }
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

.switch-mode {
    text-align: center;
    margin-top: 10px;
    
    span {
        color: #666;
    }
    
    a {
        color: #1a73e8;
        text-decoration: none;
        margin-left: 5px;
        
        &:hover {
            text-decoration: underline;
        }
    }
}

/* 表单切换动画 */
.form-switch-enter-active,
.form-switch-leave-active {
    transition: all 0.3s ease;
    position: absolute;
    width: 100%;
}

.form-switch-enter-from {
    transform: translateX(100%);
    opacity: 0;
}

.form-switch-leave-to {
    transform: translateX(-100%);
    opacity: 0;
}

/* 表单容器样式 */
.form-container {
    position: relative;
    width: 100%;
    height: 100%;
}

</style>
