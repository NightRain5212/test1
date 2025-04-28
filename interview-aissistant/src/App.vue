<template>
  <div class="left-main-menu">
    <a-menu v-model:selectedKeys="state.selectedKeys" mode="inline" :open-keys="state.openKeys" :items="items"
      @openChange="onOpenChange"></a-menu>
  </div>
  <div class="main-top">
    <div id="main-top-right-login">
      登录
    </div>
  </div>

</template>
<script setup>

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
.left-main-menu {
  height: 100%;
  border-left: 0;
  width: 20%;
  display: flex;
}

.main-top {
  height: 5%;
  display: flex;
  justify-content: flex-end;

  #main-top-right-login {
    width: 32px;
    height: 100%;
    background-color: #b4d7f0;
  }
}
</style>
