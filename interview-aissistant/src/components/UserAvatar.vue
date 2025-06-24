<template>
  <div class="avatar-wrapper" @mouseenter="showCamera = true" @mouseleave="showCamera = false">
    <n-avatar :round="true" :src="imageSrc" :size="100" color="white" @click="fileInput?.click()">
      <template v-if="!imageSrc">
        <div class="camera-hint">
          <i style="width:20px;height:20px">
            <camera_outline />
          </i>
          <span> 点击上传头像</span>
        </div>
      </template>
    </n-avatar>
    <input ref="fileInput" type="file" @change="handleChange" style="display: none" accept="image/*">
  </div>
  <!-- 2.一个用于给Cropper.js覆盖使用的img  -->
  <div class="cropper-container" v-if="show_cropper">
    <img id="cropImg" :src="cropSrc" class="cropper-box" ref="croppers">
    <div class="cropper-buttons">
      <n-button @click="confirm_cropper" type="primary">确定</n-button>
      <n-button @click="cancel_cropper" type="error">取消</n-button>
    </div>
  </div>
</template>
<script setup>
// import Cropper from 'cropperjs';
import {
  CropperCanvas, CropperImage, CropperHandle, CropperSelection, CropperGrid,
  CropperShade,
  CROPPER_CROSSHAIR
} from 'cropperjs';
import { ref,reactive, nextTick,onUnmounted } from 'vue'
import {NAvatar,NIcon}from 'naive-ui'
import { CameraOutline as camera_outline} from '@vicons/ionicons5';
import {message}from 'ant-design-vue'
import Cropper from "vue-cropperjs";
const fileInput = ref(null); // 获取 input 的 DOM
const imageSrc = ref('')//头像的图片数据
const cropSrc = ref('')//待裁剪的cropper图片数据
const show_cropper = ref(false)
const croppers = ref(null)
//裁剪区设置
const MAX_WIDTH = 400;
const MAX_HEIGHT = 400;

let CROPPER =null;//cropper实例
const handleChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // 将图片转为 base64 并显示
  const reader = new FileReader();
  reader.onload = (event) => {
    const rawimg = new Image(); // 创建临时Image对象
    rawimg.src = event.target.result;
    nextTick();
    imageSrc.value = event.target.result;
    return;
    rawimg.onload = async() => {
      console.log('原始图片加载完毕')
      // 等比缩放

      let width = rawimg.width;
      let height = rawimg.height;

        const ratio = Math.min(MAX_WIDTH / width, MAX_HEIGHT / height);
        width *= ratio;
        height *= ratio;
        console.log('width:', width, 'height:', height)

      // 创建缩放后的Canvas
      const tmp_canvas = document.createElement('canvas');
      tmp_canvas.width = width;
      tmp_canvas.height = height;
      const ctx = tmp_canvas.getContext('2d');
      ctx.drawImage(rawimg, 0, 0, width, height);

      // 将缩放后的图片传给Cropper
      show_cropper.value = true
      cropSrc.value = tmp_canvas.toDataURL('image/jpeg', 0.9);
      imageSrc.value = cropSrc.src
      await nextTick();//等待dom更新
      console.log('图片缩放完毕:', cropSrc.value)

      if (CROPPER) {
        CROPPER=null
        console.log('销毁Cropper')
      }

        if (!croppers.value) {
          console.error('未找到 cropImg 元素');
          return;
        }
        CROPPER = new Cropper(croppers.value, {
          aspectRatio: 16 / 16,      // 裁剪框的宽高比（1:1的正方形）
          viewMode: 0,              // 视图模式（0：无限制）
          minContainerWidth: width,   // 容器最小宽度
          minContainerHeight: height,  // 容器最小高度
          dragMode: 'move',         // 拖拽模式（移动画布）
        });
      
    };//原始图片加载完成之后的回调函数
  };
  reader.readAsDataURL(file);
};
function confirm_cropper() {
  //getCroppedCanvas方法可以将裁剪区域的数据转换成canvas数据
  const canvas = CROPPER.getCropperCanvas({
    maxWidth: 100,
    maxHeight: 100,
    fillColor: '#fff',
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high'
  });

  // 直接获取 Base64 字符串
  const base64Data = canvas.toDataURL('image/jpeg', 0.9); // 第二个参数是质量（0-1）
  console.log('裁剪之后的Base64数据:', base64Data);
  nextTick();
  imageSrc.value = base64Data;
  show_cropper.value = false
  message.success('上传成功')
  // CROPPER.getCroppedCanvas({
  //   maxWidth: 100,
  //   maxHeight: 100,
  //   fillColor: '#fff',
  //   imageSmoothingEnabled: true,
  //   imageSmoothingQuality: 'high',
  // }).toBlob((blob) => {
  //然后调用浏览器原生的toBlob方法将canvas数据转换成blob数据
  //之后就可以愉快的将blob数据发送至后端啦，可根据自己情况进行发送，我这里用的是axios
  //const formData = new FormData();
  // 第三个参数为文件名，可选填.
  // formData.append('croppedImage', blob/*, 'example.png' */);
  // let config = {
  //   headers: { 'Content-Type': 'multipart/form-data' }
  // }

  // this.$axios.post(flow_mission_UploadFile(), param, config)
  //   .then((response) => {
  //     console.log(response)
  //   })
  //   .catch((err) => {
  //     console.log(err)
  //   })
  //})
}
function cancel_cropper() {
  if (CROPPER) {
    CROPPER = null
    console.log('销毁Cropper')
  }
  show_cropper.value = false
  nextTick();
  imageSrc.value = '';
  console.log('imageSrc:', imageSrc.value)
}
// 组件卸载时清理
onUnmounted(() => {
  if (CROPPER) {
    CROPPER = null
    console.log('销毁Cropper')
  }
});
</script>
<style scoped lang="scss">
.avatar-wrapper {
  display: inline-block;
  position: relative;
  cursor: pointer;

  &:hover {
    .camera-hint {
      opacity: 1;
    }
  }

  .camera-hint {
    position: absolute;
    top: 50%;
    left: 30%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    color: rgb(203, 39, 39);
    opacity: 0;
    transition: opacity 0.3s;

    span {
      font-size: 12px;
      margin-top: 0px;
    }
  }
}
.cropper-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  /* 关键：基于自身宽高回退50% */
  z-index: 1000;
  width: 400px;
  height: 500px;
  //background: white;
  overflow: hidden;

  .cropper-box {
    width: 100%;
  }

  .cropper-buttons {
    position: relative;
    height: 60px;
    width: 100%;
    bottom: 0;
    margin-top: 10px;
    display: flex;
    justify-content: space-around;
    border-top: 1px solid #f0f0f0;
  }
}
</style>