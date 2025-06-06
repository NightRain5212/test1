<template>
  <div class="main-content">
    <div class="left-main-menu" ref="sidebar" :style="{ width: sidebarWidth + 'px' }">
      <div class="drag-handle" @mousedown="startDrag"></div>
      <a-menu v-model:selectedKeys="menuState.selectedKeys" mode="inline" :inlineCollapsed="collapsed"
        :open-keys="menuState.openKeys" :items="items" @openChange="onOpenChange" @select="handleMenuSelect" theme="dark"/>
    </div>
    <div class="right-main-content">
        <router-view />
    </div>
  </div>
</template>
<script setup>
// ---------------------------------------------------------------*/
//左侧主菜单
import { h, reactive,ref,onUnmounted } from 'vue';
import {
  HomeOutlined,
  PlayCircleOutlined,
  FileTextOutlined,
  HistoryOutlined,       // 替代 ClockCircleOutlined
  UnorderedListOutlined,
   SettingOutlined,
  OrderedListOutlined,
  TeamOutlined,
  InfoCircleOutlined,
  QuestionCircleOutlined,
  UserOutlined
} from '@ant-design/icons-vue';
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
  getMenuItem('主页', 'sub1', () => h(HomeOutlined), [
    getMenuItem('开始', '/', () => h(PlayCircleOutlined)),
    getMenuItem('报告', '/report', () => h(FileTextOutlined)),
  ]),
  getMenuItem('历史记录', '/history', () => h(HistoryOutlined)),
  getMenuItem('设置', '/settings', () => h(SettingOutlined)),
  getMenuItem('关于我们', 'sub4', () => h(TeamOutlined), [
    getMenuItem('Option 9', '4.1', () => h(InfoCircleOutlined)),
    getMenuItem('Option 10', '4.2', () => h(QuestionCircleOutlined)),
  ]),
  getMenuItem('我的', '/myProfile', () => h(UserOutlined)),
]);

// 菜单状态管理
const menuState = reactive({
  openKeys: ['sub1'],
  selectedKeys: ['/']
});

// 菜单展开/收起逻辑
const rootSubmenuKeys = ['sub1', 'sub4'];// 更新可展开的菜单项
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

// 侧边栏拖动逻辑
const sidebarWidth = ref(70); // 初始宽度
const minWidth = 70; // 最小宽度(只显示图标)
const maxWidth = 200; // 最大宽度
const isDragging = ref(false);
const startX = ref(0);
const startWidth = ref(0);
const sidebar = ref(null);
const collapsed = ref(true);

const startDrag = (e) => {
  isDragging.value = true;
  startX.value = e.clientX;
  startWidth.value = sidebarWidth.value;
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
};

const handleDrag = (e) => {
  if (!isDragging.value) return;
  const dx = e.clientX - startX.value;
  let newWidth = startWidth.value + dx;
  
  // 限制宽度范围
  newWidth = Math.max(minWidth, Math.min(newWidth, maxWidth));
  
  sidebarWidth.value = newWidth;
//宽度过小时，自动折叠
  if (sidebarWidth.value <= minWidth) collapsed.value = true;
  else collapsed.value = false;
};

const stopDrag = () => {
  isDragging.value = false;
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
};

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
});
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
  background-color: rgb(54, 50, 50);
}
.left-main-menu {
  position: relative;
  height: 100%;
  border-right: 1px solid #f0f0f0;
  transition: width 0.2s;
  flex-shrink: 0;//防止收缩
  overflow: hidden;//溢出隐藏
}

.drag-handle {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  cursor: col-resize;
  z-index: 1;
  
  &:hover {
    background-color: rgba(24, 144, 255, 0.1);
  }
}

.right-main-content {
  overflow: auto;
  height: 100%;
  flex:1;//这里是指占据剩余的空间
}

</style>
