<template>
  <div class="main_all">
  <div class="avatar-upload-wrapper">
    <n-upload
      ref="upload"
      action="https://www.mocky.io/v2/5e4bafc63100007100d8b70f"
      :headers="{ 'naive-info': 'hello!' }"
      :data="{ 'naive-data': 'cool! naive!' }"
      :show-file-list="false"
      @change="handleUploadChange"
    >
      <!-- 使用 n-avatar 作为上传触发器 -->
      <n-avatar
        round
        :size="48"
        :src="avatarUrl || 'https://07akioni.oss-cn-beijing.aliyuncs.com/07akioni.jpeg'"
        class="upload-avatar"
      >
        <template v-if="!avatarUrl" #default>
          <n-icon :component="UserOutlined" />
        </template>
      </n-avatar>
    </n-upload>
  </div>
  </div>
</template>

<script setup>
</script>
import {ref} from 'vue'
import { useStore } from './store';
const store = useStore();
const userInfo=ref(store.getuser())
//const avatarUrl = userInfo.value.avatarUrl; //临时测试用

import { NAvatar, NUpload, NIcon, useMessage } from 'naive-ui'
import { UserOutlined } from '@ant-design/icons-vue'

const message = useMessage()
const upload = ref(null)
const avatarUrl = ref('')

const handleUploadChange = ({ file }) => {
  if (file.status === 'done') {
    // 上传成功处理
    message.success('头像上传成功')
    // 这里应该替换为实际返回的URL
    avatarUrl.value = 'https://new-avatar-url.com/path/to/image.jpg'
  } else if (file.status === 'error') {
    message.error('头像上传失败')
  }
}

// 如果需要点击触发文件选择（备用方案）
const triggerUpload = () => {
  upload.value?.openFileDialog()
}
<style scoped lang="scss">
.main_all {
  width: 100%;
  height: 100%;
  background-color: #1a1a1a; /* 暗色背景 */
  padding: 20px;
  color:white;
}
.avatar-upload-wrapper {
  display: inline-block;
  position: relative;
}

.upload-avatar {
  cursor: pointer;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  }
}
</style>