<!-- ai版 -->
<template>
    <div class="main_all">
      <!-- 预览区域 -->
      <div class="preview">
        <video ref="videoRef" v-show="videoStream" autoplay muted playsinline></video alt='jjj'>
      </div>
      <!-- 控制按钮 -->
      <div class="controls">
        <button @click="startAudioRecording" :disabled="isRecording">
          {{ isAudioRecording ? '录音中...' : '开始录音' }}
        </button>
        <button @click="startVideoRecording" :disabled="isRecording">
          {{ isVideoRecording ? '录像中...' : '开始录像' }}
        </button>
        <button @click="stopRecording" :disabled="!isRecording">停止录制</button>
      </div>
      <!-- 录制结果 -->
      <div v-if="recordedBlob" class="result">
        <h3>录制结果</h3>
        <audio v-if="isAudio" :src="recordedUrl" controls></audio>
        <video v-else :src="recordedUrl" controls></video>
        <button @click="downloadMedia">下载</button>
      </div>
    </div>
</template>
<script setup>
  import { ref, onBeforeUnmount } from 'vue';
  const videoRef = ref(null);
  const mediaRecorder = ref(null);
  const recordedBlob = ref(null);
  const recordedUrl = ref('');
  const videoStream = ref(null);
  const isRecording = ref(false);
  const isAudioRecording = ref(false);
  const isVideoRecording = ref(false);
  const isAudio = ref(false);
  
  let chunks = [];
  
  // 获取媒体流
  const getMediaStream = async (type) => {
    try {
      const constraints = {
        audio: type === 'audio' || type === 'video',
        video: type === 'video' ? { facingMode: 'user' } : false
      };
      return await navigator.mediaDevices.getUserMedia(constraints);
    } catch (error) {
      console.error('获取媒体设备失败:', error);
      alert('无法访问媒体设备: ' + error.message);
      throw error;
    }
  };
  
  // 开始录音
  const startAudioRecording = async () => {
    try {
      const stream = await getMediaStream('audio');
      setupMediaRecorder(stream, 'audio');
      isAudioRecording.value = true;
      isRecording.value = true;
      isAudio.value = true;
    } catch (error) {
      console.error('录音启动失败:', error);
    }
  };
  
  // 开始录像
  const startVideoRecording = async () => {
    try {
      const stream = await getMediaStream('video');
      videoStream.value = stream;
      if (videoRef.value) {
        videoRef.value.srcObject = stream;
      }
      setupMediaRecorder(stream, 'video');
      isVideoRecording.value = true;
      isRecording.value = true;
      isAudio.value = false;
    } catch (error) {
      console.error('录像启动失败:', error);
    }
  };
  
  // 设置媒体录制器
  const setupMediaRecorder = (stream, type) => {
    chunks = [];
    mediaRecorder.value = new MediaRecorder(stream, {
      mimeType: type === 'audio' ? 'audio/webm' : 'video/webm'
    });
  
    mediaRecorder.value.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    };
  
    mediaRecorder.value.onstop = () => {
      recordedBlob.value = new Blob(chunks, {
        type: mediaRecorder.value.mimeType
      });
      recordedUrl.value = URL.createObjectURL(recordedBlob.value);
    };
  
    mediaRecorder.value.start(100); // 每100ms收集一次数据
  };
  
  // 停止录制
  const stopRecording = () => {
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      mediaRecorder.value.stop();
    }
    
    // 关闭所有轨道
    if (videoStream.value) {
      videoStream.value.getTracks().forEach(track => track.stop());
      videoStream.value = null;
      if (videoRef.value) {
        videoRef.value.srcObject = null;
      }
    }
  
    isRecording.value = false;
    isAudioRecording.value = false;
    isVideoRecording.value = false;
  };
  
  // 下载媒体文件
  const downloadMedia = () => {
    const a = document.createElement('a');
    a.href = recordedUrl.value;
    a.download = `recording_${new Date().toISOString()}.${isAudio.value ? 'webm' : 'mp4'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  
  // 组件卸载前清理
  onBeforeUnmount(() => {
    stopRecording();
    if (recordedUrl.value) {
      URL.revokeObjectURL(recordedUrl.value);
    }
  });
  </script>
  
  <style scoped>
  .main_all {
    width: 100%;
    height: 100vh; /* 全屏高度 */
    margin: 0 auto;
    padding: 20px;
  }

  .controls {
    width: 30%;
    height:100%;
    margin: 20px 0;
    display: flex;
    gap: 10px;
  }
  
  button {
    padding: 8px 16px;
    background: #5292d6;
    height:80px;
    cursor: pointer;
  }
  
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .preview{
    background:#3e26d8;
    width:90%;
    height:100%;
    video {
    width: 80%;
    max-height: 300px;
    background: #000;
    margin: 10px 0;
  }
  } 
  
  .result {
    margin-top: 20px;
    border-top: 1px solid #ccc;
    padding-top: 20px;
  }
  
  .result video, .result audio {
    width: 100%;
    margin: 10px 0;
  }
  </style>