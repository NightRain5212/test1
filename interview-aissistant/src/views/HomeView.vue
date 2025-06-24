<template>
  <!-- 用于显示模态框的时候判断鼠标点击是否有效 -->
  <div class="home" :style="{ 'pointer-events': isModalOpen||show_card ? 'none' : 'auto' }">

    <div class="viewarea">
      <video ref="cameraVideo" autoplay muted class="camera-pip" v-show="isCameraActive"
        disablePictureInPicture></video>
      <!-- <div v-show="!isCameraActive" class="placeholder">摄像头未开启</div>-->
      <img src="../assets/preview1.png" alt="马到成功" width=100% height=100% />
    </div>

    <div class="controlarea">
      <button v-if="!show_start" @click="show_card = true" class="btn1">
        开始面试
      </button>
      <button @click="toggleCamera" class="btn1">
        {{ isCameraActive ? '关闭摄像头' : '开启摄像头' }}
      </button>
      <button class="btn1">
        设置场景
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
        <i class="sound-icon">
          <!-- 音量开启图标（当 sliderValue > 0 时显示） -->
          <svg v-if="sliderValue > 0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
          </svg>
          <!-- 静音图标（当 sliderValue = 0 时显示） -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
          </svg>
        </i>
        <!-- Ant Design 滑块 -->
        <a-slider v-model:value="sliderValue" :min="0" :max="100" class="slider" />
      </div>
    </div>

    <Teleport to="#modal-root">
      <n-card class="startInterview" v-if="show_card">
        <!-- 步骤1：选择岗位 -->
        <div v-if="step === 1" class="step1-card">
          <div class="card11">
            <n-card title="请选择岗位" size="small">
              <n-radio-group v-model:value="jobTypeSelection" name="primaryGroup">
                <n-space vertical>
                  <n-radio v-for="item in jobTypeOptions" :key="item.value" :value="item.value" class="job_type">
                    {{ item.label }}
                  </n-radio>
                </n-space>
              </n-radio-group>
            </n-card>
          </div>

          <div class="card12">
            <n-card size="small" v-if="jobTypeSelection">
              <n-radio-group v-model:value="jobSelection" name="secondaryGroup">
                <n-grid :cols="4" :x-gap="12" :y-gap="8">
                  <n-gi v-for="item in getjobsOptions()" :key="item.value">
                    <n-radio :value="item.value" class="jobs">
                      {{ item.label }}
                    </n-radio>
                  </n-gi>
                </n-grid>
              </n-radio-group>
            </n-card>
            <n-card size="small" v-else>
            </n-card>
          </div>

          <!-- 页脚按钮 -->
          <div class="footer-buttons">
            <n-button type="default" ghost @click="show_card = false">
              我再想想
            </n-button>
            <n-button type="primary" :disabled="!jobSelection" @click="step = 2">
              继续
            </n-button>
          </div>
        </div>
        <!-- 步骤2：上传简历 -->
        <div v-if="step === 2" class="step2-card">
          <h2>上传简历</h2>
          <a-upload :customRequest="handleResumeUpload" :showUploadList="false"
            accept=".txt,.doc,.docx,.pdf,.jpg,.jpeg,.png">
            <a-button :loading="isProcessing">
              <upload-outlined></upload-outlined>
              选择文件
            </a-button>
          </a-upload>
          <a-button type="default" @click="showResumeEditor = true">没有简历？在线编辑</a-button>

        </div>
          <!-- 简历编辑器弹窗 -->
          <div v-if="showResumeEditor"  width="1200px" :footer="null">
            <ResumeEditor @submit="handleResumeEditSubmit" />
          </div>
        <template v-if="step === 2" #footer>
          <div class="footer-buttons">
            <a-button type="default" @click="step = 1">上一步</a-button>
            <a-button type="primary" @click="show_start=true" :disabled="!resumePath">开始</a-button>
          </div>
        </template>

        <!-- 步骤3：面试界面 -->
        <div v-if="step === 3" class="step3-card">
          <div class="video-section">
            <video ref="videoRef" autoplay muted></video>
            <div class="recording-indicator" v-if="isRecording">
              <div class="recording-dot"></div>
              正在录制...
            </div>
          </div>

          <div class="question-section">
            <template v-if="!isInterviewComplete">
              <h3>当前问题：</h3>
              <p class="question-text">{{ currentQuestion }}</p>
              <div class="controls">
                <a-button type="primary" @click="startInterview" v-if="!isInterviewStarted">
                  开始面试
                </a-button>
                <a-button type="primary" @click="nextQuestion" v-if="isInterviewStarted && !isInterviewComplete">
                  下一个问题
                </a-button>
              </div>
            </template>
            <template v-else>
              <h3>面试完成</h3>
              <div class="analysis-status">
                <div class="loading-spinner"></div>
                <p>正在生成分析报告...</p>
                <p class="analysis-progress">{{ analysisProgress }}</p>
              </div>
            </template>
          </div>
        </div>
      </n-card>

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
  </div>

</template>
<script setup>
import { BadgeRibbon, message } from 'ant-design-vue'
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ResumeEditor from '../components/ResumeEditor.vue'
// import{addModal,Notice} from '../components/Notice/index.js';
import { NCard, NRadio, NRadioGroup, NSpace, NButton, NDivider, NGrid, NGi,NUpload, NSpin, NIcon } from 'naive-ui'
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

const router = useRouter()
//开始面试相关
const show_card = ref(false);
const show_start = ref(false);
const showResumeEditor=ref(false);
async function toggleStart() {
  if (!isCameraActive.value){
    console.log('请打开摄像头');
    await startCamera();
  }
  if(!isRecording.value){
    console.log('请开始录音');
    await startAnswerRecording();
  }
  console.log('开始面试');
  closeCard();
}

const jobTypeSelection = ref('')
const jobSelection = ref('')

const jobTypeOptions = [
  { value: 'development', label: '开发岗' },
  { value: 'research', label: '研发岗' },
  { value: 'technical', label: '技术岗' },
  { value: 'design', label: '设计岗' },
  { value: 'testing', label: '测试岗' }
]

const jobsOptions = {
  development: [
    { value: 'frontend', label: '前端开发' },
    { value: 'backend', label: '后端开发' },
    { value: 'fullstack', label: '全栈开发' },
    { value: 'embedded', label: '嵌入式开发' },
    { value: 'desktop', label: 'C++桌面开发' },
    { value: 'mobile', label: '移动端开发' },
    { value: 'game', label: '游戏开发' }
  ],
  research: [
    { value: 'system-arch', label: '计算机系统结构' }
  ],
  technical: [
    { value: 'algorithm', label: '算法工程师' },
    { value: 'data-analysis', label: '数据分析与挖掘' }
  ],
  design: [
    { value: 'uix', label: 'UI/UX设计师' },
    { value: 'effect', label: '特效设计师' }
  ],
  testing: [
    { value: 'qa', label: '软件测试工程师' },
  ]
}

const getPrimaryLabel = () => {
  return jobTypeOptions.find(item => item.value === jobTypeSelection.value)?.label || ''
}

const getjobsOptions = () => {
  return jobsOptions[jobTypeSelection.value] || []
}

const closeCard = () => {
  show_card.value = false
}
// 面试步骤
const step = ref(1)
const resumePath = ref('')
const currentQuestion = ref('')
const isAnswerComplete = ref(false)
const isInterviewComplete = ref(false)
const currentVideoPath = ref('')

// 添加处理状态
const isProcessing = ref(false)

// 修改文件上传处理函数
async function handleResumeUpload({ file }) {
  console.log('开始上传文件:', file.name, file.type)
  isProcessing.value = true
  
  const formData = new FormData()
  formData.append('file', file.file || file)
  formData.append('job_type', jobSelection.value)
  
  try {
    const response = await axios.post('resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.code === 200) {
      resumePath.value = response.data.data.resume_path
      message.success('简历上传成功')
      
      // 保存生成的问题
      if (response.data.data.questions && response.data.data.questions.length > 0) {
        interviewQuestions.value = response.data.data.questions
        message.success('AI已生成面试问题')
        
        // 显示问题预览和确认对话框
        showConfirmInterview()
      } else {
        message.error('生成面试问题失败')
      }
    }
  } catch (error) {
    console.error('上传错误详情:', {
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers,
      error: error
    })
    
    if (error.response?.status === 422) {
      message.error('不支持的文件类型或文件格式错误：' + (error.response?.data?.detail || '仅支持txt、doc、docx、pdf、jpg、jpeg、png格式'))
    } else {
      message.error('简历上传失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    isProcessing.value = false
  }
}
function handleResumeEditSubmit(){
  console.log('yes');
}
// 添加面试问题相关的状态
const interviewQuestions = ref([])
const currentQuestionIndex = ref(0)
const isInterviewStarted = ref(false)

// 显示问题预览和确认对话框
function showConfirmInterview() {
  const previewQuestions = interviewQuestions.value.slice(0, 3).map((q, i) => `${i + 1}. ${q}`).join('\n')
  const totalQuestions = interviewQuestions.value.length
  
  addModal({
    message: `AI已根据您的简历生成了${totalQuestions}个面试问题。以下是部分问题预览：\n\n${previewQuestions}\n\n是否开始模拟面试？`,
    onConfirm: startInterview,
    onCancel: () => {
      message.info('您可以稍后点击"开始面试"按钮开始')
    }
  })
}

// 开始面试
async function startInterview() {
  try {
    // 开启摄像头
    await startCamera()
    if (!isCameraActive.value) {
      throw new Error('无法启动摄像头')
    }
    
    // 设置面试状态
    isInterviewStarted.value = true
    currentQuestionIndex.value = 0
    
    // 显示第一个问题
    showCurrentQuestion()
    
    // 自动开始录制
    startAnswerRecording()
  } catch (error) {
    message.error('启动面试失败：' + error.message)
  }
}

// 显示当前问题
function showCurrentQuestion() {
  if (currentQuestionIndex.value < interviewQuestions.value.length) {
    const question = interviewQuestions.value[currentQuestionIndex.value]
    currentQuestion.value = question
  } else {
    // 面试结束
    isInterviewComplete.value = true
    message.success('面试完成！')
    stopAnswerRecording()
    stopCamera()
  }
}

// 处理下一个问题
function nextQuestion() {
  stopAnswerRecording()
  currentQuestionIndex.value++
  isAnswerComplete.value = false
  showCurrentQuestion()
  
  // 如果还有问题，自动开始录制
  if (!isInterviewComplete.value) {
    startAnswerRecording()
  }
}

// 获取第一个问题
async function getFirstQuestion() {
  try {
    const response = await axios.post('/api/interview/next_question', {
      resume_path: resumePath.value
    })
    if (response.data.code === 200) {
      currentQuestion.value = response.data.data.question
      isAnswerComplete.value = false
      isInterviewComplete.value = response.data.data.completed
    }
  } catch (error) {
    message.error('获取面试问题失败：' + (error.response?.data?.detail || error.message))
    console.error('获取问题错误详情:', {
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers,
      error: error
    })
  }
}

// 完成面试
async function finishInterview() {
  try {
    const response = await axios.post('/api/interview/analyze', {
      video_path: lastVideoPath.value,
      resume_path: resumePath.value
    })
    if (response.data.code === 200) {
      // 跳转到报告页面
      router.push({
        path: '/report',
        query: {
          report: JSON.stringify(response.data.data)
        }
      })
    }
  } catch (error) {
    message.error('生成面试报告失败：' + (error.response?.data?.detail || error.message))
    console.error(error)
  }
}

const analysisProgress = ref('准备分析...')

// 添加分析状态和进度更新函数
async function startAnalysis() {
  try {
    analysisProgress.value = '正在分析视频...'
    // 调用后端分析接口
    const response = await axios.post('/api/analyze', {
      videoPath: currentVideoPath.value,
      jobType: jobType.value
    })
    
    if (response.data.success) {
      analysisProgress.value = '分析完成，正在生成报告...'
      // 等待2秒后跳转到报告页面
      setTimeout(() => {
        router.push({
          path: '/report',
          query: { 
            analysisId: response.data.analysisId,
            jobType: jobType.value
          }
        })
      }, 2000)
    } else {
      throw new Error(response.data.message || '分析失败')
    }
  } catch (error) {
    console.error('分析出错:', error)
    analysisProgress.value = '分析失败，请重试'
  }
}

// 修改面试完成处理函数
function handleInterviewComplete() {
  isInterviewComplete.value = true
  startAnalysis()
}

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
  stopAnswerRecording();
  isCameraActive.value = false
  cameraStream = null
  audioContext = null
  gainNode = null
  microphone = null
}
//录像相关
function toggleRecording() {
  if(isRecording.value){
    stopAnswerRecording()
    addModal({ message: '是否保存录像？', onConfirm: saveRecording });
  }else{
    startAnswerRecording()
  }
}
// 开始录制函数
function startAnswerRecording() {
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

    mediaRecorder.value.start(1000) // 每1s记录一次数据
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
function stopAnswerRecording() {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
    isRecording.value = false
    clearInterval(recordingTimer)
    message.success('回答录制完成')
    
    // 如果面试还未结束，显示下一题按钮
    if (!isInterviewComplete.value) {
      isAnswerComplete.value = true
    }
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
    message.warning('没有可保存的录制内容')
    return
  }

  try {
    const blob = new Blob(recordedChunks.value, { type: 'video/webm' })
    const formData = new FormData()
    formData.append('video', blob, 'interview.webm')
    formData.append('jobType', jobType.value)

    const response = await axios.post('/api/save-video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      currentVideoPath.value = response.data.videoPath
      islatest_save.value = true
      message.success('视频保存成功')
      // 保存成功后自动开始分析
      handleInterviewComplete()
    } else {
      throw new Error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存视频出错:', error)
    message.error('保存视频失败，请重试')
  }
}

// 组件卸载时清理
onBeforeUnmount(() => {
  stopAnswerRecording()
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

</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  border: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  background-color: #f4f4f9;
}

.viewarea {
  height: 100%;
  background: #fff;
  flex: 8;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  
  .camera {
    width: 80%;
    height: auto;
    aspect-ratio: 16/9;
    object-fit: cover;
    background: #000;
    transform: scaleX(-1);
    margin: 0 auto;
  }
  
  .camera-pip {
    position: fixed;
    right: 20px;
    bottom: 20px;
    width: 180px;
    height: auto;
    border: 1px solid #fff;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    background-color: #000;

    &:hover {
      transform: scale(1.02);
      transition: transform 0.2s;
    }
  }
  
  .placeholder {
    color: #999;
    font-size: 1rem;
  }
}

.controlarea {
  background: #fff;
  height: 100%;
  display: flex;
  flex-direction: column;
  flex: 2;
  gap: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.btn1 {
  background: #1890ff;
  width: auto;
  height: 36px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  font-size: 14px;
  transition: all 0.3s;

  &:hover {
    background: #40a9ff;
  }

  &:active {
    background: #096dd9;
  }

  &.recording {
    background: #ff4d4f;
    
    &:hover {
      background: #ff7875;
    }
    
    &:active {
      background: #d9363e;
    }
  }
}

.sound-slider {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 4px;
  background: #f5f5f5;

  .sound-icon {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    color: #595959;
  }

  .slider {
    flex-grow: 1;
  }

  .ant-slider {
    margin: 0;
  }

  .ant-slider-track {
    background-color: #1890ff;
  }

  .ant-slider-handle {
    border-color: #1890ff;
  }
}

.modal-mask {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 320px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 1000;

  .modal-header {
    background: #f5f5f5;
    height: 40px;
    width: 100%;
    display: flex;
    align-items: center;
    padding: 0 16px;
    border-bottom: 1px solid #e8e8e8;
    
    h3 {
      margin: 0;
      color: #262626;
      font-size: 14px;
    }
  }

  .modal-content {
    padding: 16px;
    background: white;
    
    p {
      margin: 0;
      color: #595959;
      font-size: 14px;
      line-height: 1.5;
    }
  }

  .modal-footer {
    padding: 8px 16px;
    background: #f5f5f5;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    border-top: 1px solid #e8e8e8;

    .btn {
      min-width: 64px;
      height: 32px;
      font-size: 14px;
      padding: 0 12px;
      border-radius: 2px;
      transition: all 0.3s;
      
      &.confirm {
        background: #1890ff;
        color: white;
        
        &:hover {
          background: #40a9ff;
        }
        
        &:active {
          background: #096dd9;
        }
      }
      
      &.cancle {
        background: #f5f5f5;
        color: #595959;
        border: 1px solid #d9d9d9;
        
        &:hover {
          background: #fafafa;
          border-color: #40a9ff;
          color: #40a9ff;
        }
        
        &:active {
          background: #f5f5f5;
          border-color: #096dd9;
          color: #096dd9;
        }
      }
    }
  }
}

.recording-duration {
  color: #595959;
  text-align: center;
  font-size: 14px;
  padding: 6px;
  background: #f5f5f5;
  border-radius: 2px;
  margin: 4px 0;
}

.startInterview {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 680px;
  min-height: 480px;
  z-index: 1000;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

  .step1-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    gap: 16px;

    .card11 {
      height: 120px;
      overflow-y: auto;

      .n-card {
        height: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        &__content {
          padding-top: 5px;
        }
      }
    }

    .card12 {
      height: 270px;
      overflow-y: auto;

      .n-card {
        height: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        &__content {
          padding-top: 5px;
        }
      }
    }

    .card11 .n-radio-group {
      .n-space {
        flex-direction: row !important;
        /* 强制横向排列 */
        flex-wrap: wrap;
        /* 允许换行 */
        gap: 8px;
        /* 设置间距 */
      }
    }

    .job_type {
      padding: 10px 16px;
      margin: 4px 0;
      border-radius: 4px;
      transition: all 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }

      &.n-radio--checked {
        background-color: #e6f4ff;
        color: #1890ff;
      }
    }

    .jobs {
      display: block;
      padding: 8px 12px;
      margin: 4px 0;
      border: 1px solid #f0f0f0;
      border-radius: 4px;
      text-align: center;
      transition: all 0.3s;

      &:hover {
        border-color: #d9d9d9;
      }

      &.n-radio--checked {
        border-color: #1890ff;
        background-color: #e6f4ff;
        color: #1890ff;
      }
    }
  }

  .step2-card {
    text-align: center;
    margin: 32px 0;
    height:100%;
    h2 {
      margin-bottom: 16px;
      font-size: 16px;
      color: #262626;
    }
  }

  .step3-card {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 16px;

    h3 {
      margin-bottom: 16px;
      text-align: center;
      font-size: 18px;
      color: #262626;
    }

    h4 {
      margin-bottom: 12px;
      color: #595959;
    }
  }

  .footer-buttons {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-top: 1px solid #f0f0f0;

    .n-button {
      min-width: 120px;
      height: 40px;
    }
  }
}

.video-section {
  position: relative;

  video {
    width: 100%;
    border-radius: 4px;
    background-color: #f5f5f5;
  }

  .recording-indicator {
    position: absolute;
    top: 8px;
    right: 8px;
    background-color: rgba(0, 0, 0, 0.75);
    color: white;
    padding: 4px 8px;
    border-radius: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
  }

  .recording-dot {
    width: 8px;
    height: 8px;
    background-color: #ff4d4f;
    border-radius: 50%;
    animation: blink 1s infinite;
  }
}

.question-section {
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 4px;

  h3 {
    margin: 0 0 12px;
    font-size: 16px;
    color: #262626;
  }

  .question-text {
    font-size: 14px;
    margin: 16px 0;
    line-height: 1.5;
    color: #595959;
  }

  .controls {
    margin-top: 16px;
    text-align: center;
  }
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.analysis-status {
  text-align: center;
  padding: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.analysis-progress {
  color: #666;
  margin-top: 10px;
  font-size: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

</style>