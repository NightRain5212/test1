<template>
  <div class="main_all">
    <n-split direction="horizontal" style="height: 100%" :max="0.55" :min="0.45">
      <template #1>
        <div class="picture-analysis">
          <!-- 视频播放器 -->
          <video ref="videoEl" :src="videoSrc" controls crossorigin="anonymous" @loadedmetadata="initAnalysis"></video>

          <!-- 分析控制 -->
          <div class="controls">
            <n-button @click="startAnalysis" :disabled="isAnalyzing">
              {{ isAnalyzing ? '分析中...' : '开始分析' }}
            </n-button>
          </div>
                     <!-- 可拖动遮盖层 -->
          <div 
            class="drag-layer"
            :style="{ height: `${dragHeight}px` }"
            @mousedown="startDrag"
          >
            <div class="drag-handle"></div>
            <div class="drag-content">
              <!-- 这里放置遮盖层内容 -->
              分析结果详情
              <div ref="chartEl" class="chart-container"></div>
            </div>
          </div>
          <!-- 图表容器 -->
          <div ref="chartEl" class="chart-container"></div>
        </div>
      </template>
      <template #2>
        <div class="video-analysis">音频分析</div>
      </template>
    </n-split>
  </div>
  <graph/>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { NButton,NSplit } from 'naive-ui'
import Graph from '../components/Graph.vue'
const videoSrc = ref('/demo-video.mp4')//直接可以访问public下的文件
const videoEl = ref(null)
const chartEl = ref(null)
const isAnalyzing = ref(false)
let chartInstance = null
let frameRequestId = null

// 初始化图表
onMounted(() => {
  chartInstance = echarts.init(chartEl.value)
})

// 清理资源
onBeforeUnmount(() => {
  if (frameRequestId) cancelAnimationFrame(frameRequestId)
  if (chartInstance) chartInstance.dispose()
})

// 视频元数据加载完成后初始化
const initAnalysis = () => {
  console.log(`视频信息: ${videoEl.value.videoWidth}x${videoEl.value.videoHeight}, 时长: ${videoEl.value.duration}s`)
}

// 开始分析
const startAnalysis = async () => {
  if (!videoEl.value) return
  
  isAnalyzing.value = true
  const data = []
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  // 设置Canvas尺寸与视频一致
  canvas.width = videoEl.value.videoWidth
  canvas.height = videoEl.value.videoHeight
  
  // 逐帧分析函数
  const analyzeFrame = () => {
    if (videoEl.value.paused || videoEl.value.ended) {
      isAnalyzing.value = false
      return
    }
    
    // 1. 绘制当前帧到Canvas
    ctx.drawImage(videoEl.value, 0, 0, canvas.width, canvas.height)
    
    // 2. 获取帧图像数据
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    
    // 3. 计算帧平均亮度
    const brightness = calculateFrameBrightness(imageData.data)
    
    // 4. 记录数据 (时间戳, 亮度值)
    data.push({
      time: videoEl.value.currentTime,
      value: brightness
    })
    
    // 5. 更新图表
    updateChart(data)
    
    // 6. 继续下一帧
    frameRequestId = requestAnimationFrame(analyzeFrame)
  }
  
  // 开始播放并分析
  try {
    await videoEl.value.play()
    frameRequestId = requestAnimationFrame(analyzeFrame)
  } catch (err) {
    console.error('播放失败:', err)
    isAnalyzing.value = false
  }
}

// 计算帧亮度 (简化算法)
const calculateFrameBrightness = (pixelData) => {
  let sum = 0
  for (let i = 0; i < pixelData.length; i += 4) {
    // RGB转亮度公式
    sum += 0.299 * pixelData[i] + 0.587 * pixelData[i+1] + 0.114 * pixelData[i+2]
  }
  return sum / (pixelData.length / 4) / 255 // 归一化到0-1
}

// 更新图表
const updateChart = (data) => {
  chartInstance.setOption({
    title: { text: '视频帧亮度分析' },
    tooltip: {
      trigger: 'axis',
      formatter: params => {
        return `时间: ${params[0].data.time.toFixed(2)}s<br>亮度: ${params[0].data.value.toFixed(4)}`
      }
    },
    xAxis: {
      type: 'value',
      name: '时间(s)'
    },
    yAxis: {
      type: 'value',
      name: '亮度',
      min: 0,
      max: 1
    },
    series: [{
      data: data.map(item => [item.time, item.value]),
      type: 'line',
      smooth: true,
      areaStyle: {}
    }]
  })
}

const dragHeight = ref(200); // 初始高度
    const isDragging = ref(false);
    const startY = ref(0);
    const startHeight = ref(0);

    const startDrag = (e) => {
      isDragging.value = true;
      startY.value = e.clientY;
      startHeight.value = dragHeight.value;
      document.addEventListener('mousemove', handleDrag);
      document.addEventListener('mouseup', stopDrag);
    };

    const handleDrag = (e) => {
      if (!isDragging.value) return;
      const deltaY = startY.value - e.clientY;
      const newHeight = startHeight.value + deltaY;
      
      // 限制高度范围（最小50px，最大占屏幕70%）
      const maxHeight = window.innerHeight * 0.7;
      dragHeight.value = Math.max(50, Math.min(newHeight, maxHeight));
    };

    const stopDrag = () => {
      isDragging.value = false;
      document.removeEventListener('mousemove', handleDrag);
      document.removeEventListener('mouseup', stopDrag);
    };

</script>

<style scoped lang="scss">
.main_all {
  width: 100%;
  height: 100%;
  padding:10px;
  background-color: #938a8a; /* 暗色背景 */ 
    display: flex;
  flex-direction: row;
}
.picture-analysis { 
    flex:8;
}
.video-analysis {
    background-color: #d99b9b; /* 侧边栏背景 */
    flex: 4;
}

.video-analysis {
  max-width: 800px;
  margin: 0 auto;
}

video {
  width: 100%;
  background: #000;
  margin-bottom: 20px;
}

.controls {
  margin: 15px 0;
  text-align: center;
}

.chart-container {
  width: 100%;
  height: 400px;
  border: 1px solid #eee;
  border-radius: 4px;
}


/* 可拖动层样式 */
.picture-analysis {
  position: relative;
  height: 100%;
  overflow: hidden; /* 防止内容溢出 */
}

.drag-layer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  border-top: 1px solid #ddd;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  transition: height 0.2s ease;
  z-index: 10;
}

.drag-handle {
  height: 16px;
  background: #f0f0f0;
  cursor: ns-resize;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drag-handle::after {
  content: "≡";
  color: #666;
  font-size: 20px;
}

.drag-content {
  padding: 10px;
  height: calc(100% - 16px); /* 减去把手高度 */
  overflow-y: auto;
}
</style>