<template>
    <div class="main_all">
        <n-grid :y-gap="0" :cols="1">
            <n-grid-item :style="{ 'background-color': '#c6b9b9' }">
                <div class="header">
                    <div class="header_left">
                        <user-avatar />
                    </div>
                    <div class="header_right">
                        <!-- 用户名行 -->
                        <div class="userinfo">
                            <span style="user-select: none;">用户名:</span>
                            <n-input v-if="editing.username" v-model:value="tempUsername" 
                            style=" width: 200px;height:30px;margin-left: 10px; border-color: #1890ff;border-radius: 4px;  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);" 
                            @blur=" is_saveEdit('username')" />
                            <n-text v-else
                                style="margin-left: 10px; width: 200px; display: inline-block;user-select: none;">
                                {{ username }}
                            </n-text>
                            <n-button text @click="toggleEdit('username')" style="margin-left: 5px;">
                                <n-icon size="18">
                                    <Edit />
                                </n-icon>
                            </n-button>
                            <n-button text @click="copyToClipboard(username)" style="margin-left: 5px;">
                                <n-icon size="18">
                                    <Copy />
                                </n-icon>
                            </n-button>
                        </div>

                        <!-- 邮箱行 -->
                        <div class="userinfo">
                            <span style="user-select: none;">邮箱:</span>
                            <n-input v-if="editing.email" v-model:value="tempEmail"
                                style="width: 200px;height:30px; margin-left: 10px;" @blur="is_saveEdit('email')" />
                            <n-text v-else
                                style="margin-left: 10px; width: 200px; display: inline-block; user-select: none;">
                                {{ email }}
                            </n-text>
                            <n-button text @click="toggleEdit('email')" style="margin-left: 5px;">
                                <n-icon size="18">
                                    <Edit />
                                </n-icon>
                            </n-button>
                            <n-button text @click="copyToClipboard(username)" style="margin-left: 5px;">
                                <n-icon size="18">
                                    <Copy />
                                </n-icon>
                            </n-button>
                        </div>
                    </div>
                </div>

                <!-- 个人简介 -->
                <div class="userinfo">
                    <span style="user-select: none; padding-left:20px">个人简介:</span>
                    <n-input v-if="editing.bio" v-model:value="tempBio" 
                        style="width: 300px;height:30px; margin-left: 10px; vertical-align: top;"
                         @blur="is_saveEdit('bio')" />
                    <n-text v-else style="margin-left: 10px; width: 300px; display: inline-block;user-select: none;">
                        {{ bio }}
                    </n-text>
                    <n-button text @click="toggleEdit('bio')" style="margin-left: 5px; vertical-align: top;">
                        <n-icon size="18">
                            <Edit />
                        </n-icon>
                    </n-button>
                    <n-button text @click="copyToClipboard(username)" style="margin-left: 5px;">
                        <n-icon size="18">
                            <Copy />
                        </n-icon>
                    </n-button>
                </div>

            </n-grid-item>

            <n-grid-item :style="{ 'background-color': 'black' }">
                <div class="content">
                    个人
                </div>
            </n-grid-item>
        </n-grid>
    </div>

    <Teleport to="#modal-root">
        <!-- 内容区域启用指针事件 -->
        <div v-if="isModalOpen" class="modal-mask" style="pointer-events: auto;" @click.stop>
            <div class="modal-header">
                <h3>提示</h3>
            </div>
            <div class="modal-content">
                <p>{{ currentModal.message }}</p>
            </div>
            <div class="modal-footer">
                <button @click="handleConfirm" class="btn confirm">是</button>
                <button @click="handleCancel" class="btn cancle">否</button>
            </div>
        </div>
    </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import UserAvatar from '../components/UserAvatar.vue';
import { message } from 'ant-design-vue'
import { NGrid, NGridItem, NButton, NIcon, NInput, NText } from 'naive-ui'
import { Edit, Copy } from '@vicons/carbon'
import axios from "../utils/axios";
import { useStore } from '../store';
import rules from '../utils/rules'
const store = useStore();
const userInfo = ref(store.getUser())
//const avatarUrl = userInfo.value.avatarUrl; //临时测试用
// 用户数据
// const username = ref('张三')
// const email = ref('zhangsan@example.com')
// const bio = ref('还没有添加任何自我介绍~~~')
const username = userInfo.value.username;
const email = userInfo.value.email;
const bio = userInfo.value.bio;

// 临时编辑数据
const tempUsername = ref('')
const tempEmail = ref('')
const tempBio = ref('')

// 编辑状态
const editing = ref({
    username: false,
    email: false,
    bio: false
})

// 切换编辑状态
const toggleEdit = (field) => {
    if(editing.value[field]==false){
        editing.value['username'] = false
        editing.value['email'] = false
        editing.value['bio'] = false
    }
    editing.value[field] = !editing.value[field]
    if (editing.value[field]) {
        // 进入编辑模式时，保存当前值到临时变量
        tempUsername.value = username.value
        tempEmail.value = email.value
        tempBio.value = bio.value
    }
}
const is_saveEdit=(field)=> {
    let flag = false
    if (field === 'username' && tempUsername.value !== username.value) flag = true
    if (field === 'email' && tempEmail.value !== email.value) flag = true
    if (field === 'bio' && tempBio.value !== bio.value) flag = true
    if (flag) {
        addModal({ message: '是否保存修改？', onConfirm: saveEdit , onCancel: () =>{editing.value[field] = false}} )
    }else {
        editing.value[field] = false
    }
}

function validate() { 
    let is_username = true;
    let is_email = true;
    if (username.value!='')
        is_username = rules.usernameRegex.test(tempUsername.value)
    if (email.value!='')
        rules.emailRegex.test(tempEmail.value)
    return is_username && is_email
}
// 保存编辑
async function saveEdit() {
    const isValid = validate()
    if (!isValid) {
     message.error('信息格式不正确！') 
     return
    }
    const preferences = ref({
        id:localStorage.getItem('id'),
        username: tempUsername.value,
        email: tempEmail.value,
       preference:{
        bio: tempBio.value
       } 
    })
    try {
        const res = await axios.post('/api/user/update_info', preferences.value)
        if (res?.code == 0) {
            message.error('更改失败')
            return
        }
        username.value = tempUsername.value
        email.value = tempEmail.value
        bio.value = tempBio.value
        message.success('更改成功')
    } catch (error) {
        console.log(error)
        message.error('更改失败')
    }
    editing.value['username'] = false
    editing.value['email'] = false
    editing.value['bio'] = false
}
// 复制到剪贴板函数
const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
        .then(() => {
            message.success('复制成功')
        })
}

//弹窗队列相关
// 状态
const modalQueue = ref([]);
const currentModal = ref(null);
const isModalOpen = ref(false);

// 方法
const addModal = (modalConfig) => {
  modalQueue.value.push(modalConfig);
  if (!currentModal.value) showNextModal();
};
const showNextModal = () => {
  if (modalQueue.value.length === 0) {
    currentModal.value = null;
    isModalOpen.value = false;
    return;
  }
  currentModal.value = modalQueue.value.shift();
  isModalOpen.value = true;
};

const handleConfirm = () => {
  currentModal.value?.onConfirm?.();
  showNextModal();
};

const handleCancel = () => {
  currentModal.value?.onCancel?.();
  showNextModal();
};
</script>
<style scoped lang="scss">
.main_all {
    width: 100%;
    height: 100%;
    //background-color: #5e5b5b; /* 暗色背景 */
    padding: 20px;
    color: white;
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
        height: 100%;
        padding: 10px;
        /* 内边距 */
        box-sizing: border-box;
        /* 包含内边距和边框 */
    }
}
.content {
    height: 200px;
    background-color: #534f4f;
}

.userinfo {
    font-size: auto;
    color: white;
    margin: 10px 0 10px 10px;
    display: flex;
    align-items: center;
}
.modal-mask {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 360px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 999;
  .modal-header {
    background: #f5f5f5;
    height: 48px;
    width: 100%;
    display: flex;
    align-items: center;
    padding: 0 16px;
    border-bottom: 1px solid #e8e8e8;
    
    h3 {
      margin: 0;
      color: #262626;
      font-size: 16px;
    }
  }
  .modal-content {
    padding: 24px;
    background: white;
    
    p {
      margin: 0;
      color: #595959;
      font-size: 14px;
      line-height: 1.5;
    }
  }
.modal-footer {
    padding: 12px 16px;
    background: #f5f5f5;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    border-top: 1px solid #e8e8e8;

    .btn {
      min-width: 80px;
      height: 32px;
      font-size: 14px;
      padding: 0 15px;
      border-radius: 4px;
      transition: all 0.3s;
      
      &.confirm {
        background: #b8b9ba;
        color: white;
        
        &:hover {
          background: #d5d8da;
        }
        
        &:active {
          background: #d1d4d6;
        }
      }
      
      &.cancle {
        background: rgb(151, 146, 146);
        color: white;
        
        &:hover {
          background: #d5d8da;
        }
        
        &:active {
          background: #d1d4d6;
        }
      }
    }
  }
}
</style>