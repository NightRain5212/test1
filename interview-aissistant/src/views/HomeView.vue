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
        <div class="icon">
          <svg v-if="sliderValue > 0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
          </svg>
        </div>
        <div class="slider">
          <a-slider v-model:value="sliderValue" :min="0" :max="100" />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const isCameraActive = ref(false)
const cameraVideo = ref(null)
const sliderValue = ref(30) // 默认设为中间值
let cameraStream = null
let audioContext = null
let gainNode = null// 用于控制音量
let microphone = null// 用于连接麦克风

// 监听滑块值变化
watch(sliderValue, (newVal) => {
  updateVolume(newVal)
})
function updateVolume(value) {
  if (!gainNode) return
  const volume = value / 100// 将滑块值(0-100)转换为音量系数(0-1)
  gainNode.gain.value = volume
}
async function toggleCamera() {
  if (isCameraActive.value) {
    stopCamera()
  } else {
   await startCamera()
  }

}
async function startCamera() {
  try {
    // 获取摄像头和麦克风媒体流
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment'
      },
      audio: true // 启用音频
    })

    // 初始化Web Audio API
    audioContext = new (window.AudioContext || window.webkitAudioContext)()
    microphone = audioContext.createMediaStreamSource(stream)
    gainNode = audioContext.createGain()
    
    // 连接音频节点：麦克风 → 增益控制 → 目的地
    microphone.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    // 设置初始音量
    updateVolume(sliderValue.value)

    cameraVideo.value.srcObject = stream
    isCameraActive.value = true
    cameraStream = stream
  } catch (error) {
    console.error('设备访问错误:', error)
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop())
    
    // 断开音频节点
    if (microphone && gainNode) {
      microphone.disconnect()
      gainNode.disconnect()
    }
    
    if (audioContext) {
      audioContext.close()
    }
  }
  
  if (cameraVideo.value) {
    cameraVideo.value.srcObject = null
  }
  
  isCameraActive.value = false
  cameraStream = null
  audioContext = null
  gainNode = null
  microphone = null
}

onBeforeUnmount(() => {
  stopCamera()
})
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
  background: rgb(47, 45, 45);
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
  display: flex;
  align-items: center;
  /* 垂直居中 */
  gap: 10px;
  /* 图标和滑块间距 */
  padding: 8px 12px;

  .icon {
    flex-shrink: 0;
    /* 防止图标被压缩 */
    width: 24px;
    height: 24px;
    color: #e2e7ebe9;
  }

  .slider {
    flex-grow: 1;
    /* 滑块占据剩余空间 */
  }

  /* 调整antd滑块样式（可选） */
  .ant-slider {
    margin: 0;
  }
}
</style>