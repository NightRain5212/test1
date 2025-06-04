<template>
    <!-- 头像展示（点击触发文件选择） -->
    <n-avatar round :size="72" :src="avatarUrl" class="user-avatar" @click="triggerFileInput">
        <template #default v-if="!avatarUrl">
            <UserOutlined style="font-size: 72px;" />
        </template>
    </n-avatar>

    <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleFileSelect" />
    <!-- 裁剪模态框 -->
    <n-modal v-model:show="showCropModal">
        <n-card style="width: 300px">
            <template #header>裁剪头像</template>
            <div class="cropper-container">
                <img ref="cropperImage" src="" alt="未选择图片！" />
            </div>
            <template #footer>
                <n-space justify="end">
                    <n-button @click="showCropModal = false">取消</n-button>
                    <n-button type="primary" @click="confirmCrop">确认</n-button>
                </n-space>
            </template>
        </n-card>
    </n-modal>
</template>
<script setup>
import { ref, onMounted, onUnmounted,nextTick,watch } from 'vue';
import {UserOutlined} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue'
import {NAvatar,NButton,NModal,NCard,NSpace} from 'naive-ui'
import Cropper from 'cropperjs';
const fileInput = ref(null);
const cropperImage = ref(null);
const avatarUrl = ref('');
const showCropModal = ref(false);
let cropper = null;

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click();//html的input标签内置方法，点击后触发文件选择
};

// 选择文件后显示裁剪框
const handleFileSelect = (e) =>{
    const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (event) => {
    showCropModal.value = true;//展示裁剪框
    nextTick(() => {
      initCropper(event.target.result);//初始化裁剪器
    });
  };
  reader.readAsDataURL(file);
}

// 初始化裁剪器
 const initCropper =async (imageSrc) => {
  try {
    // 确保目标元素存在且已挂载
    await nextTick();
    if (!cropperImage.value) {
      throw new Error('Cropper target element not found');
    }

    // 清理旧实例
    if (cropper?.destroy) {
      cropper.destroy();
    }

    // 初始化新实例
    cropper = new Cropper(cropperImage.value, {
      aspectRatio: 1,
      viewMode: 1,
      autoCropArea: 1,
      ready() {
        console.log('Cropper ready');
      }
    });

    // 设置图片源（必须在初始化后）
    cropper.replace(imageSrc);
  } catch (err) {
    console.error('Cropper init failed:', err);
    message.error('图片加载失败');
  }
};

// 确认裁剪
const confirmCrop = () => {
  try {
    if (!cropper?.getCroppedCanvas) {
      throw new Error('Cropper not initialized');
    }

    const canvas = cropper.getCroppedCanvas({
      width: 200,
      height: 200,
      fillColor: '#fff'
    });

    if (!canvas) {
      throw new Error('Canvas generation failed');
    }

    avatarUrl.value = canvas.toDataURL('image/png');
    showCropModal.value = false;

    // 上传逻辑
    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append('avatar', blob, 'avatar.png');
      // 调用上传API
    }, 'image/png', 0.9);
    
  } catch (err) {
    console.error('Crop failed:', err);
    message.error('裁剪失败: ' + err.message);
  }
};

// 清理裁剪实例
onUnmounted(() => {
  if (cropper?.destroy) {
    cropper.destroy();
    cropper = null;
  }
});

// 模态框关闭时清理
watch(showCropModal, (val) => {
  if (!val && cropper?.destroy) {
    cropper.destroy();
    cropper = null;
  }
});
</script>

<style scoped lang="scss">
//裁剪框样式
.cropper-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.cropper-container img {
  display: block;
  max-width: 100%;
  touch-action: none; /* 移动端必需 */
}
//用户头像区
.user-avatar {
  cursor: pointer;
  transition: opacity 0.3s;
  &:hover {
    opacity: 0.8;
  }
}
</style>