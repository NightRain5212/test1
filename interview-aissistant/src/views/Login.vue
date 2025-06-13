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
            <div v-if="display_loginform" class="loginform-box" @submit.prevent="login" moUseleave="hoverClose = false" 
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
                        <input type="text" id="username" placeholder="请输入4-30位用户名" v-model="logininput_info.username"
                            required minlength="4" maxlength="30">
                    </div>

                    <div class="input-box">
                        <label for="password">密码:</label>
                        <input type="password" id="password" placeholder="请输入8-12位密码" v-model="logininput_info.password"
                            required minlength="8" maxlength="12">
                    </div>

                    <div class="login-submit-btn">
                        <button class="login-btn" @click="login">Login</button>
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
                            v-model="registerinput_info.username"
                            required minlength="4" maxlength="30">
                    </div>

                    <div class="input-box">
                        <label for="reg-email">邮箱:</label>
                        <input type="email" id="reg-email" 
                            placeholder="请输入邮箱" 
                            v-model="registerinput_info.email"
                            required>
                    </div>

                    <div class="input-box">
                        <label for="reg-password">密码:</label>
                        <input type="password" id="reg-password" 
                            placeholder="请输入8-12位密码" 
                            v-model="registerinput_info.password"
                            required minlength="8" maxlength="12">
                    </div>

                    <div class="input-box">
                        <label for="reg-confirm">确认密码:</label>
                        <input type="password" id="reg-confirm" 
                            placeholder="请再次输入密码" 
                            v-model="registerinput_info.confirmPassword"
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
import axios, {isTokenExpired} from "../utils/axios";
import { useRouter } from 'vue-router'
const route = useRouter() // 获取全局路由实例，一个app只有一个route实例
import{Modal,message} from "ant-design-vue";
import { debounce } from 'lodash-es';// 防抖函数
import rules from "../utils/rules";
import {  useStore } from '../store'
const store = useStore() // 获取全局状态管理实例，一个app只有一个store实例
const logininput_info = ref({
    username: '',
    password: '',
})
// 注册表单数据
const registerinput_info = ref({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
});
const hoverClose = ref(false)//一个退出按钮的变量
// 是否显示登陆界面
const display_loginform = ref(false)
// 控制表单模式
const isRegisterMode = ref(false)
function clear_login() {
    logininput_info.value = {
        username: '',
        password: '',
    }
}
function clear_register() {
    registerinput_info.value = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    } 
}
// 更新登陆界面状态
const openloginform = () => {
    display_loginform.value = true;
     clear_login(),clear_register();
}
function closeLoginForm (){
    display_loginform.value = false; 
    clear_login(),clear_register()
    // 延迟重置表单高度
    setTimeout(() => {
        const formBox = document.querySelector('.loginform-box');
        if (formBox) {
            formBox.style.height = '300px';
        }
    }, 300);
}

async function performLogin(input_info) {
    const hideLoading = message.loading('登录中...', 0);

    console.log('登录信息:', input_info);
    try {
        // 1. 验证用户是否存在
        const res = await axios.get('/user/get_info', {
            params: {
                username: input_info.username
            }
        });
       console.log('返回体:', res)

        // 用户不存在时的处理
        if (!res?.data) {
            return await handleUserNotExist(input_info);
        }
        // 2. 密码验证
        if (!res.data?.password || input_info.password !== res.data.password) {
            message.error(res.data?.password ? '密码错误' : '密码无效');
            return false;
        }
        // 3. 登录流程
        return await handleLoginSuccess(input_info,res.data);
    } catch (error) {
        handleLoginError(error);
        return false;
    } finally {
        hideLoading();
    }
}

// 用户不存在处理
async function handleUserNotExist(input_info) {
    message.error('用户不存在');
    
    return new Promise((resolve) => {
        Modal.confirm({
            title: '用户未注册',
            content: `用户"${input_info.username}"未注册，是否立即注册？`,
            okText: '是',
            cancelText: '否',
            onOk() {
                switchMode();  // 切换到注册模式
                resolve('registered'); // 特殊返回值表示注册成功
            },
            onCancel() {
                message.info('已取消注册');
                resolve(false);
            }
        });
    });
}

// 登录成功处理
async function handleLoginSuccess(input_info,res) {
    try {
        const tokenRes = await axios.post('/auth/login', input_info);
        console.log('请求令牌，返回：', tokenRes)
        if (!tokenRes?.data?.access_token) {
            message.error('登录失败: 令牌获取异常');
            return false;
        }
        // 存储令牌
        localStorage.setItem('accessToken', tokenRes.data.access_token);
        localStorage.setItem('refreshToken', tokenRes.data.refresh_token);
        localStorage.setItem('id', res.id);//用户id存储在localStorage中

        store.setUser(res)
        // 异步下载文件（不阻塞登录流程）
        DownloadFile()
            .then(() => message.success('文件加载完成'))
            .catch(() => message.warning('文件加载失败'));
        startTokenRefresh(tokenRes.data.expired_in);
        message.success(`欢迎回来，${input_info.username}!`);
        display_loginform.value = false; // 关闭登录界面
        return true;
    } catch (error) {
        handleLoginError(error);
        return false;
    }
}

// 错误处理
function handleLoginError(error) {
    console.log('登录错误:', error);
    if (error.response?.status === 401) {
        message.error('认证失败!');
    } else {
        message.error('登录错误!');
    }
}

// 防抖登录
const debouncedLogin = debounce(async (input_info,resolve) => {
    const result = await performLogin(input_info);
    resolve(result);
}, 1000, { leading: true, trailing: false });//多次点击，第一次无间隔，最后一次无效

// 防抖注册
const debouncedRegister = debounce(async (input_info,resolve) => {
    const result = await register(input_info);
    resolve(result);
}, 1000, { leading: true, trailing: false });//多次点击，第一次无间隔，最后一次无效

// 对外暴露的登录函数
async function login() {
    const input_info={...logininput_info.value}//响应体解包
    // 输入验证
    function validateInput() {
        if (!input_info.username || !input_info.password) {
            message.info('用户名或密码不能为空');
            return false;
        }

        if (!rules.usernameRegex.test(input_info.username)) {
            message.error('用户名必须为4-30位字母/汉字/数字/连字符组合，且不能以数字开头');
            return false;
        }

        if (!rules.passwordRegex.test(input_info.password)) {
            message.error('密码必须为8-12位，包含字母和数字，可加特殊字符(!@#$%^&*等)');
            return false;
        }
        return true;
    }
    //resolve
    return new Promise((resolve) => {
        if (!validateInput()) {
            return resolve(false);
        }
        debouncedLogin(input_info,resolve);
    });
}
// 注册函数
async function register(input_info) {
    console.log("register:", input_info);
    try {
        const res = await axios.post('/auth/register', input_info)//post可以传对象
        if (!res.data) {
            message.info('用户已注册！')
        }//规定返回data为null则用户已注册
        else {
            message.success('注册成功！')
        }
        // 切换到登录模式
        isRegisterMode.value = false
        // 预填充用户名
        logininput_info.value.username = input_info.username
        logininput_info.value.password = input_info.password
        clear_register()
    } catch (error) {
        console.log(error)
        message.error(`注册失败！ ${error.response?.data?.message || error.message||''}`);
    }
}
// accessToken令牌刷新函数
async function refreshTokens() {
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
        // 无有效refreshToken，跳转登录
        message.warning('令牌已失效，请重新登录！');
        route.push('/login');
        return;
    }

    try {
        // 1. 用refreshToken获取新accessToken
        //第二个参数是请求体,第三个参数是配置，这里设置请求头
        const res = await axios.post('/auth/refresh',{refresh_token: refreshToken});

        // 2. 更新本地令牌
        localStorage.setItem('accessToken', res.data.accessToken);

        // 3. 重新发起之前的请求（如果有）
        if (res.data?.refreshToken) {
            localStorage.setItem('refreshToken', res.data.refreshToken);
        }

    } catch (error) {
        console.log(error);
        if (error.response.status === 401) {
            message.error('登录已过期，请重新登录');
        } else {
            message.error('未知错误，请稍后再试')
        }
        localStorage.clear();
        route.push('/login');
    }
}

// 启动定时令牌刷新
let refreshInterval;
function startTokenRefresh(vaild_duration) {
    // 清除旧定时器
    if (refreshInterval) clearInterval(refreshInterval);

    // 每5分钟检查一次（根据实际token有效期调整）,setInterval是内置函数，接收两个参数，第一个是要执行的函数，第二个是执行时间间隔
    refreshInterval = setInterval(async () => {
        const accessToken = localStorage.getItem('accessToken');

        // 如果accessToken不存在或已过期
        if (!accessToken || isTokenExpired(accessToken)) {
            console.log('获取accessToken')
                await refreshTokens();
        }
    }, vaild_duration); // 以毫秒为单位
}

// 注册处理函数
async function handleRegister(e) {
    e.preventDefault(); // 阻止默认提交行为
    const input_info={...registerinput_info.value}
    // 输入验证
    function register_validateInput() {
        if (!rules.usernameRegex.test(input_info.username)) {
            message.error('用户名必须为4-30位字母/汉字/数字/连字符组合，且不能以数字开头');
            return false;
        }

        if (!rules.passwordRegex.test(input_info.password)) {
            message.error('密码必须为8-12位，包含字母和数字，可加特殊字符(!@#$%^&*等)');
            return false;
        }

        if (input_info.password !== input_info.confirmPassword) {
            message.error('两次输入的密码不一致')
            return false;
        }
        if (!input_info.username || !input_info.password || 
            !input_info.email || !input_info.confirmPassword) {
            message.error('请填写所有必填项')
            return false;
        }
        if (!rules.passwordRegex.test(input_info.email)) {
            message.error('邮箱格式不正确')
            return false;
        }
        return true;
    }
    
    //resolve
    console.log('输入合法');
    return new Promise((resolve) => {
        if (!register_validateInput()) {
            return resolve(false);
        }
        debouncedRegister(input_info, resolve);
    });
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
       clear_register()
        // 设置注册表单高度
        formBox.style.height = '450px';
    } else {
        clear_login()
        // 设置登录表单高度
        formBox.style.height = '300px';
    }
}
//上传url地址，然后从临时目录下载文件到本地
async function downloadAndUnzip(zipUrl) {
  try {
    const response = await fetch(zipUrl);
    const blob = await response.blob();
    const zip = new JSZip();
    const contents = await zip.loadAsync(blob);
    
    const files = [];
    for (const filename in contents.files) {
      if (!contents.files[filename].dir) {
        const fileBlob = await contents.files[filename].async('blob');
        files.push({
          name: filename,
          blob: fileBlob,
          url: URL.createObjectURL(fileBlob)
        });
      }
    }
    return files;
  } catch (error) {
    console.error('解压失败:', error);
    throw error;
  }
}

async function DownloadFile() {
  try {
    // 1. 获取下载URL列表（假设store.geturl()返回URL数组）
    const urls = store.geturl();
    
    // 2. 调用后端下载接口
    const response = await axios.post("/api/download", {
      urls: urls,
      max_files: 10 // 可配置
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      }
    });
    
    // 3. 下载并解压ZIP
    const zipFiles = await downloadAndUnzip(response.data.zip_url);
    
    // 4. 按原始顺序排序
    zipFiles.sort((a, b) => {
      const aIdx = parseInt(a.name.split('_')[0]);
      const bIdx = parseInt(b.name.split('_')[0]);
      return aIdx - bIdx;
    });
    
    // 5. 重构文件信息
    const files = zipFiles.map((file, index) => ({
      originalUrl: response.data.files[index].original_url,
      name: file.name.split('_').slice(1).join('_'), // 移除序号
      blob: file.blob,
      url: file.url,
      type: store._getFileType(file.name)
    }));
    
    // 6. 存储到store
    store.saveFiles(files);
    
    // 7. 清理临时URL（可选）
    setTimeout(() => {
      files.forEach(file => URL.revokeObjectURL(file.url));
    }, 5000);
    
    return files;
  } catch (error) {
    console.error('文件下载失败:', error);
    throw error;
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
// /* 电视机扩散模式 */
// /*transition的name自动匹配以name为前缀 */
// .fade-enter-active, .fade-leave-active {
//   transition: all 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55); /* 弹性动画 */
// }

// .fade-enter-from, .fade-leave-to {
//   opacity: 0;/* 透明度 */
//   clip-path: circle(0% at 50% 50%); /* 从中心点收缩为 0 */
//   transform: scale(0.8); /* 初始缩小 */
// }

// .fade-enter-to, .fade-leave-from {
//   opacity: 1;/* 透明度 */
//   clip-path: circle(100% at 50% 50%); /* 展开至全屏 */
//   transform: scale(1); /* 恢复原大小 */
// }
/* 渐显模式 */
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
        /*去除输入框的轮廓线*/
        outline: none;
        border: solid 2px skyblue;
        border-radius: 5px;
        padding-left: 20px;
        transition: border-color 0.3s ease;
        
        &:focus {
            border-color: #1a73e8;
            box-shadow: 0 0 0 2px rgba(26,115,232,0.2);
        }
    }

    .login-title h2 {
        font-size: 100px;
    }
    label {
        /*固定标签宽度*/
        min-width: 80px; 
        text-align: right;
        margin-right: 10px;
        color: #333;
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
    transform: translateX(100%);/* 从右侧进入 */
    opacity: 0;/* 初始透明度 */
}

.form-switch-leave-to {
    transform: translateX(-100%);/* 从左侧离开 */
    opacity: 0;/* 离开时的透明度 */
}

/* 表单容器样式 */
.form-container {
    position: relative;
    width: 100%;
    height: 100%;
}

</style>
