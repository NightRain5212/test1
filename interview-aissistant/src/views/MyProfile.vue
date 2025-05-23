<template>
    <div class="main_all">
        <n-grid :y-gap="0" :cols="1">
           <n-grid-item :style="{ 'background-color': '#c6b9b9' }">
                <div class="header">
                    <div class="header_left">
                        <user-avatar />
                    </div>
                    <div class="header_right">
                        <div class="userinfo">用户名:</div>
                        <div class="userinfo">邮箱:</div>
                    </div>
                </div>
                <div class="userinfo">个人简介:</div>
            </n-grid-item>
            <n-grid-item :style="{ 'background-color': 'black' }">
                <div class="content">
                    个人
                </div>
            </n-grid-item>
        </n-grid>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted,nextTick,watch } from 'vue';
import UserAvatar from '../components/UserAvatar.vue';
import { message } from 'ant-design-vue'
import{NGrid,NGridItem} from 'naive-ui'

import { useStore } from '../store';
const store = useStore();
const userInfo=ref(store.getUser())
//const avatarUrl = userInfo.value.avatarUrl; //临时测试用

</script>
<style scoped lang="scss">
.main_all {
  width: 100%;
  height: 100%;
  //background-color: #5e5b5b; /* 暗色背景 */
  padding: 20px;
  color:white;
}
.header {
    display: flex;
    height: 100px;
    flex-direction: row;

    .header_left {
        width: 100px;
        height: 100%;
        /* 宽度为50% */
        padding: 10px;
        /* 内边距 */
        box-sizing: border-box;
        /* 包含内边距和边框 */
        text-align: center;
    }

    .header_right {
        flex: 1;
        height:100%;
        padding: 10px;
        /* 内边距 */
        box-sizing: border-box;
        /* 包含内边距和边框 */
    }
}
.content{
    height:200px;
    background-color: #534f4f;
}
.userinfo{ 
    font-size: auto;
    color: white;
}
</style>