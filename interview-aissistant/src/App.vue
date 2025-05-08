<template>
  <div class="main-content">
    <div class="left-main-menu">
      <a-menu
        v-model:selectedKeys="menuState.selectedKeys"
        mode="inline"
        :open-keys="menuState.openKeys"
        :items="items"
        @openChange="onOpenChange"
        @select="handleMenuSelect"
      />
    </div>
    <div class="right-main-content">
      <router-view />
    </div>
  </div>
</template>
<script setup>
/ ---------------------------------------------------------------*/
//左侧主菜单
import { h, reactive } from 'vue';
import { MailOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons-vue';
import { useRouter } from 'vue-router';
import { useStore } from './store';
const store = useStore();
const router = useRouter();
// 菜单项生成器
const getMenuItem = (label, key, icon = null, children = null) => ({
  key,
  icon,
  children,
  label
});

// 菜单配置
const items = reactive([
  getMenuItem('主页', 'sub1', () => h(MailOutlined), [//MailOutlined是ant-design-vue的图标
    getMenuItem('开始', '/'),  // 直接使用路由路径作为key
    getMenuItem('报告', '/login'),
  ]),
  getMenuItem('历史', 'sub2', () => h(AppstoreOutlined), [
    getMenuItem('Option 5', '2.1'),
    getMenuItem('Option 6', '2.2'),
  ]),
  getMenuItem('设置', 'sub3', () => h(AppstoreOutlined), [
    getMenuItem('Option 5', '3.1'),
    getMenuItem('Option 6', '3.2'),
  ]),
  getMenuItem('关于我们', 'sub4', () => h(SettingOutlined), [
    getMenuItem('Option 9', '4.1'),
    getMenuItem('Option 10', '4.2'),
  ]),
    getMenuItem('我的', '/myProfile', () => h(SettingOutlined), []),
]);

// 菜单状态管理
const menuState = reactive({
  openKeys: ['sub1'],
  selectedKeys: []
});

// 菜单展开/收起逻辑
const rootSubmenuKeys = ['sub1', 'sub2', 'sub3', 'sub4','myProfile'];
//主要为了实现菜单的特效
const onOpenChange = (openKeys) => {
  const latestOpenKey = openKeys.find(key => !menuState.openKeys.includes(key));
  menuState.openKeys = latestOpenKey && rootSubmenuKeys.includes(latestOpenKey) 
    ? [latestOpenKey] 
    : openKeys;
};

// 菜单项选择处理
const handleMenuSelect = ({ key }) => {
  if (key.startsWith('/')) {
    router.push(key);
    menuState.selectedKeys = [key];
  }
};
</script>

<style scoped lang="scss">/*使用scss,允许嵌套类*/
/* 导入字体 */
@import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;1,500&display=swap');
/*处理布局*/
.main-content {
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
  box-sizing: border-box;
  font-family: "Poppins", sans-serif;
  display: flex; /* 只需要写一次 */
}

.left-main-menu {
  flex: 2;  /* 占1份 */
}

.right-main-content {
  flex: 9;  /* 占9份 */
}

.left-main-menu {
  height: 100%;
  border-left: 0;
  display: flex;
  overflow: auto; /* 允许菜单滚动 */
}

</style>
