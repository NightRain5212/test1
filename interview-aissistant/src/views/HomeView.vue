<template>
  <!-- 用于显示模态框的时候判断鼠标点击是否有效 -->
  <div class="home"  :style="{ 'pointer-events': isModalOpen ? 'none' : 'auto' }">
    <div class="viewarea">
      <!-- 摄像头视频显示区域 -->
      <video ref="cameraVideo" autoplay muted class="camera" v-show="isCameraActive"></video>
      <div v-show="!isCameraActive" class="placeholder">摄像头未开启</div>
    </div>
    <div class="controlarea">
      <button @click="toggleCamera" class="btn1">
        {{ isCameraActive ? '关闭摄像头' : '开启摄像头' }}
      </button>
      <button @click="toggleRecording" class="btn1" v-if="isCameraActive" :class="{ 'recording': isRecording }">
        {{ isRecording ? '停止录制' : '开始录制' }}
      </button>
      <!-- 显示录制时长 -->
      <div v-if="isRecording" class="recording-duration">
        {{ recordingDuration }}
      </div>
      <button v-if="isCameraActive" class="btn1" @click="saveRecording">
        保存
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
  <!-- vue提供组件---将模态框渲染到 body 末尾 -->
  <Teleport to="body">
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
import { message } from 'ant-design-vue'
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
//摄像相关
const isCameraActive = ref(false)
const cameraVideo = ref(null)
const sliderValue = ref(30) // 默认设为中间值

// 添加录制相关的状态
const mediaRecorder = ref(null)
const recordedChunks = ref([])
const isRecording = ref(false)
const recordingStartTime = ref(null)
const recordingDuration = ref('00:00')
let recordingTimer = null
const islatest_save = ref(false);//最新的录像是否保存

let cameraStream = null
let audioContext = null
let gainNode = null// 浏览器内置的音频处理节点
let microphone = null// 用于连接麦克风

//声音相关
// 监听滑块值变化
watch(sliderValue, (newVal) => {
  updateVolume(newVal)
})
function updateVolume(value) {
  if (!gainNode) return
  const volume = value / 100// 将滑块值(0-100)转换为音量系数(0-1)
  gainNode.gain.value = volume
}
//摄像头相关
async function toggleCamera() {
  if (isCameraActive.value) {
    if(!islatest_save.value){
      addModal({ message: '录像未保存，是否保存录像？', onConfirm: saveRecording });
    }
    addModal({ message: '是否关闭摄像头？', onConfirm: stopCamera });
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
  // 断开音频节点
  if (microphone && gainNode) {
    microphone.disconnect()
    gainNode.disconnect()
  }

  if (audioContext) {
    audioContext.close()
  }
  if (cameraStream) {
    // 停止流中的所有轨道
    cameraStream.getTracks().forEach(track => track.stop())
  }

  if (cameraVideo.value) {
    cameraVideo.value.srcObject = null
  }
  stopRecording();
  isCameraActive.value = false
  cameraStream = null
  audioContext = null
  gainNode = null
  microphone = null
}
//录像相关
function toggleRecording() {
  if(isRecording.value){
    stopRecording()
    addModal({ message: '是否保存录像？', onConfirm: saveRecording });
  }else{
    startRecording()
  }
}
// 开始录制函数
function startRecording() {
  if (!cameraStream) {
    message.error('请先开启摄像头')
    return
  }

  try {
    recordedChunks.value = []
    mediaRecorder.value = new MediaRecorder(cameraStream)
    
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.value.push(event.data)
      }
    }

    mediaRecorder.value.start(200) // 每200ms记录一次数据
    isRecording.value = true
    recordingStartTime.value = Date.now()
    updateRecordingDuration()
    message.success('开始录制')
  } catch (error) {
    console.error('录制失败:', error)
    message.error('录制失败')
  }
} 

// 停止录制
function stopRecording(){
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
    isRecording.value = false
    clearInterval(recordingTimer)
    message.success('录制已停止')
  }
}

// 更新录制时长
function updateRecordingDuration() {
  recordingTimer = setInterval(() => {
    const duration = Math.floor((Date.now() - recordingStartTime.value) / 1000)
    const minutes = Math.floor(duration / 60).toString().padStart(2, '0')
    const seconds = (duration % 60).toString().padStart(2, '0')
    recordingDuration.value = `${minutes}:${seconds}`
  }, 1000)
}

// 保存录像函数
async function saveRecording() {
  if (recordedChunks.value.length === 0) {
    message.warning('没有可保存的录像')
    return
  }

  try {
    // // 停止录制
    // if (isRecording.value) {
    //   stopRecording()
    // }

    // 创建Blob对象
    const blob = new Blob(recordedChunks.value, {
      type: 'video/webm'
    })

    // 生成下载链接
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    a.href = url
    a.download = `recording-${timestamp}.webm`
    
    // 触发下载
    document.body.appendChild(a)
    a.click()
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      recordedChunks.value = []
    }, 100)

    message.success('录像已保存')
    return true
  } catch (error) {
    console.error('保存失败:', error)
    message.error('保存失败')
    return false
  }
}

// 组件卸载时清理
onBeforeUnmount(() => {
  stopRecording()
  stopCamera()
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }
})

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

// // 处理模态框关闭
// function Close(forceClose = false) {
//   if (forceClose) {
//     stopCamera();
//     showText1.value = false;
//   } else {
//     showText1.value = false;
//   }
// }

// // 处理保存并关闭
// async function saveAndClose() {
//   try {
//     await saveRecording();
//     stopCamera();
//     showText1.value = false;
//     message.success('录像已保存');
//   } catch (error) {
//     message.error('保存失败');
//     console.error('保存失败:', error);
//   }
//   stopCamera();
// }

// // 更新关闭摄像头逻辑
// async function toggleCamera() {
//   if (isCameraActive.value) {
//     // 如果有未保存的录像，显示确认框
//    if (hasUnsavedRecording) {
//       showText1.value = true;
//     } else {
//       stopCamera();
//     }
//   } else {
//     await startCamera();
//   }
// }
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
  height: auto; /* 高度自适应 */
  aspect-ratio: 16/9; /* 固定宽高比（常用摄像头比例） */
  object-fit: contain; /* 改为contain以完整显示画面 */
  background: #000;
  transform: scaleX(-1);
  margin: 0 auto; /* 水平居中 */
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

.btn1 {
  background: rgb(234, 230, 230);
  width: auto;
  height: 40px;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background: rgb(220, 215, 215);
  }
  &.recording {
    background: #231e1e;
    color: white;
    
    &:hover {
      background: #786767;
    }
    
    &:active {
      background: #bab6b6;
    }
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

.recording-duration {
  color: #fff;
  text-align: center;
  font-size: 1.2rem;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  margin: 8px 0;
}
</style>