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
const change_display_loginform = ()=> {
  display_loginform.value = ! display_loginform.value;
}
//用户输入用户名和密码，查询信息。并且支持自动注册。使用jwt双令牌来刷新token，结合本地存储用户信息
async function login(username, password) {
    //首先在本地查看是否存在该用户信息，如果存在，直接返回用户信息。
    const access_token = localStorage.getItem('accesstoken');
    const refresh_token = localStorage.getItem('refreshtoken');
    //如果不存在，向服务器发送请求，查询用户信息。
    if (!access_token) {
        const res=await axios.get('/api/getuserinfo', {params: {username, password}});
        if (res.status===200) {
            //如果查询到用户信息，将用户信息存储到本地。
            localStorage.setItem('accesstoken', res.data.accesstoken);
            localStorage.setItem('refreshtoken', res.data.refreshtoken); 
            localStorage.setItem('userinfo', res.data.userinfo);
            return res.data.userinfo;
        }
        //如果查询不到用户信息，返回错误信息。
       
    } else if (token) {
        //如果令牌没有过期，直接返回用户信息。
        //否则刷新令牌，再次验证
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
