<template>
    <div class="main-all">
        <div class="loginform-box">
            <div class="form-header">
                <h2>{{ isRegisterMode ? '注册账号' : '欢迎回来' }}</h2>
                <p>{{ isRegisterMode ? '创建一个新账号开始使用' : '使用您的账号登录系统' }}</p>
            </div>

            <Transition name="form-switch" mode="out-in">
                <!-- 登录表单 -->
                <form autocomplete="off" v-if="!isRegisterMode" class="login-form">
                    <div class="input-box">
                        <n-input
                            v-model:value="logininput_info.username"
                            type="text"
                            placeholder="请输入用户名"
                            :maxlength="30"
                            round
                        >
                            <template #prefix>
                                <n-icon><UserOutlined /></n-icon>
                            </template>
                        </n-input>
                    </div>

                    <div class="input-box">
                        <n-input
                            v-model:value="logininput_info.password"
                            type="password"
                            placeholder="请输入密码"
                            :maxlength="12"
                            round
                            show-password-on="click"
                        >
                            <template #prefix>
                                <n-icon><LockOutlined /></n-icon>
                            </template>
                        </n-input>
                    </div>

                    <div class="login-submit-btn">
                        <n-button type="primary" round block @click="login">
                            登录
                        </n-button>
                    </div>

                    <div class="switch-mode">
                        <span>还没有账号？</span>
                        <a href="#" @click.prevent="switchMode">立即注册</a>
                    </div>
                </form>

                <!-- 注册表单 -->
                <form autocomplete="off" v-else @submit.prevent="handleRegister" class="register-form">
                    <div class="input-box">
                        <n-input
                            v-model:value="registerinput_info.username"
                            type="text"
                            placeholder="请输入4-30位用户名"
                            :maxlength="30"
                            round
                        >
                            <template #prefix>
                                <n-icon><UserOutlined /></n-icon>
                            </template>
                        </n-input>
                    </div>

                    <div class="input-box">
                        <n-input
                            v-model:value="registerinput_info.email"
                            type="email"
                            placeholder="请输入邮箱"
                            round
                        >
                            <template #prefix>
                                <n-icon><MailOutlined /></n-icon>
                            </template>
                        </n-input>
                    </div>

                    <div class="input-box">
                        <n-input
                            v-model:value="registerinput_info.password"
                            type="password"
                            placeholder="请输入8-12位密码"
                            :maxlength="12"
                            round
                            show-password-on="click"
                        >
                            <template #prefix>
                                <n-icon><LockOutlined /></n-icon>
                            </template>
                        </n-input>
                    </div>

                    <div class="input-box">
                        <n-input
                            v-model:value="registerinput_info.confirmPassword"
                            type="password"
                            placeholder="请再次输入密码"
                            :maxlength="12"
                            round
                            show-password-on="click"
                        >
                            <template #prefix>
                                <n-icon><LockOutlined /></n-icon>
                            </template>
                        </n-input>
                    </div>

                    <div class="login-submit-btn">
                        <n-button type="primary" round block @click="handleRegister">
                            注册
                        </n-button>
                    </div>

                    <div class="switch-mode">
                        <span>已有账号？</span>
                        <a href="#" @click.prevent="switchMode">返回登录</a>
                    </div>
                </form>
            </Transition>
        </div>
    </div>
</template>

<script setup>
import { h, ref, onMounted } from 'vue';
//登录
import axios, {isTokenExpired} from "../utils/axios";
import { useRouter, useRoute } from 'vue-router'
const route = useRouter() // 获取全局路由实例
const currentRoute = useRoute() // 获取当前路由信息
import{Modal,message} from "ant-design-vue";
import { debounce } from 'lodash-es';// 防抖函数
import rules from "../utils/rules";
import {  useStore } from '../store'
const store = useStore() // 获取全局状态管理实例，一个app只有一个store实例
import { NButton, NInput, NIcon } from 'naive-ui'
import { 
    PersonOutline as UserOutlined,
    LockClosedOutline as LockOutlined,
    MailOutline as MailOutlined 
} from '@vicons/ionicons5'
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
// 切换登录/注册模式
function switchMode() {
    isRegisterMode.value = !isRegisterMode.value;
    if (isRegisterMode.value) {
        clear_register();
    } else {
        clear_login();
    }
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
        localStorage.setItem('id', res.id);

        store.setUser(res)
        store.login(); // 设置登录状态
        
        // 异步下载文件（不阻塞登录流程）
        DownloadFile()
            .then(() => message.success('文件加载完成'))
            .catch(() => message.warning('文件加载失败'));
        
        startTokenRefresh(tokenRes.data.expired_in);
        message.success(`欢迎回来，${input_info.username}!`);
        
        // 获取重定向路径并跳转
        const redirect = currentRoute.query.redirect || '/';
        route.push(redirect);
        
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

// 上传url地址，然后从临时目录下载文件到本地
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

// 监听路由变化，自动显示登录窗口
onMounted(() => {
    console.log('当前路由参数：', currentRoute.query);
    // 如果是从其他页面跳转来的，自动显示登录窗口
    if (currentRoute.query.redirect || currentRoute.query.showLogin === 'true') {
        switchMode();
    }
});
</script>

<style scoped lang="scss">
.main-all {
    height: 100vh;
    width: 100%;
    padding: 0;
    margin: 0;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, 
        rgba(91, 36, 122, 0.45) 0%, 
        rgba(27, 206, 223, 0.55) 100%
    );
    backdrop-filter: blur(10px);
}

.loginform-box {
    position: relative;
    width: 480px;
    padding: 50px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;

    .form-header {
        text-align: center;
        margin-bottom: 40px;

        h2 {
            font-size: 32px;
            color: #333;
            margin-bottom: 16px;
            font-weight: 600;
        }

        p {
            color: #666;
            font-size: 16px;
            line-height: 1.5;
        }
    }
}

.input-box {
    margin-bottom: 24px;

    :deep(.n-input) {
        .n-input__input-el {
            height: 48px;
            font-size: 16px;
        }

        .n-input__prefix {
            margin-left: 12px;
        }

        .n-input__input-wrapper {
            padding-left: 44px;
        }
    }
}

.login-submit-btn {
    margin: 32px 0;

    :deep(.n-button) {
        height: 48px;
        font-size: 16px;
        font-weight: 500;
    }
}

.switch-mode {
    text-align: center;
    margin-top: 24px;
    
    span {
        color: #666;
        font-size: 14px;
    }
    
    a {
        color: #18a058;
        text-decoration: none;
        margin-left: 8px;
        font-weight: 500;
        font-size: 14px;
        
        &:hover {
            text-decoration: underline;
        }
    }
}

.form-switch-enter-active,
.form-switch-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: absolute;
    width: 100%;
}

.form-switch-enter-from {
    opacity: 0;
    transform: translateX(30px);
}

.form-switch-leave-to {
    opacity: 0;
    transform: translateX(-30px);
}

.login-form,
.register-form {
    position: relative;
    width: 100%;
}
</style>
