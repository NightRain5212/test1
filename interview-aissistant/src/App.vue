<template>
  <div class="main-content">
    <div class="left-main-menu">
      <a-menu v-model:selectedKeys="state.selectedKeys" mode="inline" :open-keys="state.openKeys" :items="items"
        @openChange="onOpenChange"></a-menu>
    </div>
    <!-- <div v-if="state.selectedKeys[0]=='1.1'">
      <routeLink to="/views/HomeView.vue">
        <router-view></router-view>
      </routeLink>
    </div> -->
    <div class="right-main-content">
      <login></login>
    </div>
  </div>
</template>
<script setup>
/ ---------------------------------------------------------------*/
//左侧主菜单
import { h, reactive } from 'vue';
import { MailOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons-vue';
import login from './views/Login.vue';

import { useStore } from './store';
const store = useStore();
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
  getItem('主页', 'sub1', () => h(MailOutlined), [
    getItem('开始', '1.1'),
    getItem('报告', '1.2'),
  ]),
  getItem('历史', 'sub2', () => h(AppstoreOutlined), [
    getItem('Option 5', '5'),
    getItem('Option 6', '6'),
    getItem('Submenu', 'sub3', null, [getItem('Option 7', '7'), getItem('Option 8', '8')]),
  ]),
    getItem('设置', 'sub3', () => h(AppstoreOutlined), [
    getItem('Option 5', '5'),
    getItem('Option 6', '6'),
    getItem('Submenu', 'sub6', null, [getItem('Option 7', '7'), getItem('Option 8', '8')]),
  ]),
  getItem('关于我们', 'sub4', () => h(SettingOutlined), [
    getItem('Option 9', '9'),
    getItem('Option 10', '10'),
    getItem('Option 11', '11'),
    getItem('Option 12', '12'),
  ]),
]);
const state = reactive({
  rootSubmenuKeys: ['sub1', 'sub2', 'sub3','sub4'],
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
