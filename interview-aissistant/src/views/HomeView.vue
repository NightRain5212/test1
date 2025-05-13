<template>
  <div class="home">
    <div class="viewarea">
      <!-- 摄像头视频显示区域 -->
      <video ref="cameraVideo" autoplay muted class="camera" v-show="isCameraActive"></video>
      <div v-show="!isCameraActive" class="placeholder">摄像头未开启</div>
    </div>
    <div class="controlarea">
      <button @click="toggleCamera" class="btn">
        {{ isCameraActive ? '关闭摄像头' : '开启摄像头' }}
      </button>
      <div class="sound-slider">
        <div class="icon" v-if="sliderValue > 0"><svg >
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
          </svg>
        </div>
        <div class="icon" v-if="sliderValue == 0"><svg>
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
          </svg>
        </div>
          <a-slider class="silder" v-model:value="sliderValue" :min="0" :max="20" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount,computed} from 'vue'

const isCameraActive = ref(false)
const cameraVideo = ref(null)
let cameraStream = null// 摄像头流

// 开启/关闭摄像头
async function toggleCamera() {
  if (isCameraActive.value) {
    stopCamera()
  } else {
    try { await startCamera() }
    catch (error) {
      message.warn('未开启摄像头！')
    }
  }
}

// 启动摄像头
async function startCamera() {
  try {
    // 获取摄像头媒体流（默认使用前置摄像头）
    //浏览器内置
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment'  // 关键参数：强制使用后置摄像头
      },
      audio: false // 如果需要音频可以设为true
    })

    // 将流赋值给video元素
    cameraVideo.value.srcObject = stream
    isCameraActive.value = true
    cameraStream = stream
  } catch (error) {
    console.error('摄像头访问错误:', error)
  }
}

// 关闭摄像头
function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop())
  }// 停止所有轨道
  if (cameraVideo.value) {
    cameraVideo.value.srcObject = null// 释放视频源
  }
  isCameraActive.value = false
  cameraStream = null
}

// 组件卸载时自动关闭摄像头
onBeforeUnmount(() => {
  stopCamera()
})

//声音滑动条
const sliderValue = ref(0);

</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  border: 0;
}

.viewarea {
  height: 100%;
  background: rgb(211, 205, 205);
  flex: 8;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  
  .camera {
    width: 80%;
    height: 80%;
    object-fit: cover; // 填充整个区域
    background: #000;
    transform: scaleX(-1); // 镜像翻转（使画面更自然）
  }
  
  .placeholder {
    color: #666;
    font-size: 1.2rem;
  }
}

.controlarea {
  background: rgb(249, 127, 127);
  height: 100%;
  display: flex;
  flex-direction: column; // 垂直排列按钮
  flex: 2;
  gap: 10px; // 按钮间距
  padding: 10px;
}

.btn {
  background: rgb(234, 230, 230);
  width: 100%;
  height: 40px;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background: rgb(220, 215, 215);
  }
}
.sound-slider {
  position: relative;
  padding: 0px 30px;
  flex: display;
  display: flex;
  flex-grow: row;

  & :first-child {
    left: 5px;
  }

  //匹配第一个子元素
  & :last-child {
    right: 5px;
  }

  .icon {
    width: 16px;
    height: 16px;
  }
}
// .anticon {
//   position: absolute;
//   top: -2px;
//   width: 16px;
//   height: 16px;
//   line-height: 1;
//   font-size: 16px;
//   color: rgba(0, 0, 0, 0.25);
</style>