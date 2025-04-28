<template>
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
  <div class="main-container">
    <div class="left-main-menu">
      <a-menu v-model:selectedKeys="state.selectedKeys" mode="inline" :open-keys="state.openKeys" :items="items"
        @openChange="onOpenChange"></a-menu>
    </div>
    <div class="right-main-content">
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
  </div>
</template>
<script setup>
/ ---------------------------------------------------------------*/
//登录
import { ref } from 'vue';

// 是否显示登陆界面
const display_loginform = ref(false)

// 更新登陆界面状态
const change_display_loginform = ()=> {
  display_loginform.value = ! display_loginform.value;
}

/ ---------------------------------------------------------------*/
//左侧主菜单
import { h, reactive } from 'vue';
import { MailOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons-vue';
function getItem(label, key, icon, children, type) {
  return {
    key,
    icon,
    children,
    label,
    type,
  };
}
const items = reactive([
  getItem('Navigation One', 'sub1', () => h(MailOutlined), [
    getItem('Option 1', '1'),
    getItem('Option 2', '2'),
    getItem('Option 3', '3'),
    getItem('Option 4', '4'),
  ]),
  getItem('Navigation Two', 'sub2', () => h(AppstoreOutlined), [
    getItem('Option 5', '5'),
    getItem('Option 6', '6'),
    getItem('Submenu', 'sub3', null, [getItem('Option 7', '7'), getItem('Option 8', '8')]),
  ]),
  getItem('Navigation Three', 'sub4', () => h(SettingOutlined), [
    getItem('Option 9', '9'),
    getItem('Option 10', '10'),
    getItem('Option 11', '11'),
    getItem('Option 12', '12'),
  ]),
]);
const state = reactive({
  rootSubmenuKeys: ['sub1', 'sub2', 'sub4'],
  openKeys: ['sub1'],
  selectedKeys: [],
});
const onOpenChange = openKeys => {
  const latestOpenKey = openKeys.find(key => state.openKeys.indexOf(key) === -1);
  if (state.rootSubmenuKeys.indexOf(latestOpenKey) === -1) {
    state.openKeys = openKeys;
  } else {
    state.openKeys = latestOpenKey ? [latestOpenKey] : [];
  }

};

</script>
<style scoped>
/* 导入字体 */
@import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;1,500&display=swap');
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "poppins", sans-serif;
}

.main-container  {
  display:flex;
  position: relative;
  background: linear-gradient(
    to right,
    rgba(235, 65, 139, 0.833),
    rgba(151, 40, 236, 0.84)
  );
  background-position: center;
  background-size: cover;
  height: 90%;
  width: 100%;
}

.left-main-menu, .right-main-content{
  flex: 1,9; /* 左右空间分配 */
}

.left-main-menu {
  height: 100%;
  border-left: 0;
  width: 20%;
  display: flex;
}

header {
  background: transparent;
  position: absolute;
  z-index: 100; /* 确保导航栏在最上层 */
  top: 0;
  left: 0;
  height: 10%;
  width: 100%;
}

header nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  width: 100%;
  background: rgba(255, 254, 254, 0.336);
  user-select: none;
}

header .links-box {
  background: transparent;
  width: 80%;
  height: 100%;
}

header .nav-login-box {
  display: flex;
  background: transparent;
  width: 20%;
  height: 100%;
  font-size: 30px;
  align-items: center;
  justify-content: center;
  color: #fff;
}

header .nav-login-box:hover {
  cursor: pointer;
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
