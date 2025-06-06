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
              <!-- 分析结果详情 -->
              <div v-if="analysisResult" class="analysis-results">
                <div class="score-section">
                  <h3>综合得分</h3>
                  <div class="total-score">{{ analysisResult.scores.total.toFixed(2) }}</div>
                  <div class="score-breakdown">
                    <div class="score-item">
                      <span>视频表现：</span>
                      <span>{{ analysisResult.scores.video.toFixed(2) }}</span>
                    </div>
                    <div class="score-item">
                      <span>语音表现：</span>
                      <span>{{ analysisResult.scores.voice.toFixed(2) }}</span>
                    </div>
                    <div class="score-item">
                      <span>内容表现：</span>
                      <span>{{ analysisResult.scores.text.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>
                <div ref="chartEl" class="chart-container"></div>
              </div>
              <div v-else class="no-results">
                点击"开始分析"按钮开始分析视频
              </div>
            </div>
          </div>
          <!-- 图表容器 -->
          <div ref="chartEl" class="chart-container"></div>
        </div>
      </template>
      <template #2>
        <div class="video-analysis">
          <h3>详细分析报告</h3>
          <div v-if="analysisResult" class="analysis-details">
            <!-- 视频分析结果 -->
            <div class="analysis-section">
              <h4>视频分析</h4>
              <div class="detail-item">
                <span>姿态稳定性：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.video_data.posture_stability * 100).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.video_data.posture_stability)"
                />
              </div>
              <div class="detail-item">
                <span>手势频率：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.video_data.hand_movement * 100).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.video_data.hand_movement)"
                />
              </div>
              <div class="detail-item">
                <span>面部表情：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.video_data.eyebrow_raise * 100).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.video_data.eyebrow_raise)"
                />
              </div>
            </div>

            <!-- 语音分析结果 -->
            <div class="analysis-section">
              <h4>语音分析</h4>
              <div class="detail-item">
                <span>语速：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.voice_data.speech_rate * 20).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.voice_data.speech_rate / 5)"
                />
              </div>
              <div class="detail-item">
                <span>音量变化：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.voice_data.energy_variation * 100).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.voice_data.energy_variation)"
                />
              </div>
              <div class="detail-item">
                <span>语调变化：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.voice_data.pitch_variation * 100).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.voice_data.pitch_variation)"
                />
              </div>
            </div>

            <!-- 文本分析结果 -->
            <div class="analysis-section">
              <h4>内容分析</h4>
              <div class="detail-item">
                <span>关键词匹配：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.text_data.keyword_count * 10).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.text_data.keyword_count / 10)"
                />
              </div>
              <div class="detail-item">
                <span>内容连贯性：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.text_data.content_coherence * 100).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.text_data.content_coherence)"
                />
              </div>
              <div class="detail-item">
                <span>简历相关性：</span>
                <n-progress
                  type="line"
                  :percentage="(analysisResult.details.text_data.resume_similarity * 100).toFixed(0)"
                  :color="getProgressColor(analysisResult.details.text_data.resume_similarity)"
                />
              </div>
            </div>

            <!-- AI建议 -->
            <div class="analysis-section">
              <h4>AI面试官建议</h4>
              <div class="suggestions">
                {{ analysisResult.suggestions }}
              </div>
            </div>
          </div>
          <div v-else class="no-analysis">
            暂无分析结果
          </div>
        </div>
      </template>
    </n-split>
  </div>
  <graph/>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { NButton, NSplit, NProgress } from 'naive-ui'
import Graph from '../components/Graph.vue'
import { message } from 'ant-design-vue'

const videoSrc = ref('')
const videoEl = ref(null)
const chartEl = ref(null)
const isAnalyzing = ref(false)
const analysisResult = ref(null)
let chartInstance = null

// 初始化图表
onMounted(() => {
  // 获取最新录制的视频路径
  const lastRecordedVideo = localStorage.getItem('lastRecordedVideo')
  if (lastRecordedVideo) {
    // 从完整路径中提取文件名（处理 Windows 路径）
    const filename = lastRecordedVideo.split('\\').pop().split('/').pop()
    // 构建视频URL
    videoSrc.value = `http://localhost:8000/videos/${filename}`
  }
  
  chartInstance = echarts.init(chartEl.value)
})

// 清理资源
onBeforeUnmount(() => {
  if (chartInstance) chartInstance.dispose()
})

// 视频元数据加载完成后初始化
const initAnalysis = () => {
  console.log(`视频信息: ${videoEl.value.videoWidth}x${videoEl.value.videoHeight}, 时长: ${videoEl.value.duration}s`)
}

// 保存历史记录
async function saveToHistory(result) {
  try {
    const userId = localStorage.getItem('userId') // 从localStorage获取用户ID
    if (!userId) {
      message.error('请先登录')
      return
    }

    const response = await fetch('http://localhost:8000/api/history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: parseInt(userId),
        action: '视频分析',
        result: result
      })
    })

    if (!response.ok) {
      throw new Error('保存历史记录失败')
    }

    const data = await response.json()
    console.log('历史记录保存成功:', data)
  } catch (error) {
    console.error('保存历史记录失败:', error)
    message.error('保存历史记录失败')
  }
}

// 开始分析
async function startAnalysis() {
  if (!videoSrc.value) {
    message.error('请先选择要分析的视频')
    return
  }

  try {
    isAnalyzing.value = true
    message.loading({ content: '正在分析视频...', key: 'analysis' })

    const lastRecordedVideo = localStorage.getItem('lastRecordedVideo')
    if (!lastRecordedVideo) {
      throw new Error('未找到视频文件路径')
    }

    // 从视频URL中提取文件名
    const filename = videoSrc.value.split('/').pop()
    if (!filename) {
      throw new Error('无法获取视频文件名')
    }

    const response = await fetch('http://localhost:8000/api/analyze/video', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        video_path: filename,
        resume_text: ''
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '分析请求失败')
    }

    const result = await response.json()
    if (!result.data) {
      throw new Error('服务器返回的数据格式不正确')
    }

    analysisResult.value = result.data

    // 保存分析结果到历史记录
    await saveToHistory(result.data)

    message.success({ content: '分析完成', key: 'analysis' })
    // 更新图表
    updateChart(result.data)

  } catch (error) {
    console.error('分析失败:', error)
    message.error({ 
      content: `分析失败: ${error.message}`, 
      key: 'analysis',
      duration: 5
    })
  } finally {
    isAnalyzing.value = false
  }
}

// 更新图表
function updateChart(data) {
  if (!chartInstance) return
  
  const option = {
    title: {
      text: '面试表现雷达图',
      textStyle: {
        color: '#333'
      }
    },
    radar: {
      indicator: [
        { name: '视频表现', max: 100 },
        { name: '语音表现', max: 100 },
        { name: '内容表现', max: 100 },
        { name: '姿态稳定', max: 100 },
        { name: '语速控制', max: 100 },
        { name: '表达清晰', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          data.scores.video * 100,
          data.scores.voice * 100,
          data.scores.text * 100,
          data.details.video_data.posture_stability * 100,
          (5 - Math.abs(data.details.voice_data.speech_rate - 3)) * 20,
          data.details.text_data.content_coherence * 100
        ],
        name: '得分'
      }]
    }]
  }
  
  chartInstance.setOption(option)
}

// 获取进度条颜色
function getProgressColor(value) {
  if (value >= 0.8) return '#18a058'
  if (value >= 0.6) return '#2080f0'
  if (value >= 0.4) return '#f0a020'
  return '#d03050'
}

const dragHeight = ref(200)
const isDragging = ref(false)
const startY = ref(0)
const startHeight = ref(0)

const startDrag = (e) => {
  isDragging.value = true
  startY.value = e.clientY
  startHeight.value = dragHeight.value
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

const handleDrag = (e) => {
  if (!isDragging.value) return
  const deltaY = startY.value - e.clientY
  const newHeight = startHeight.value + deltaY
  
  const maxHeight = window.innerHeight * 0.7
  dragHeight.value = Math.max(50, Math.min(newHeight, maxHeight))
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}
</script>

<style scoped lang="scss">
.main_all {
  width: 100%;
  height: 100%;
  padding:10px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  background-color: #f4f4f9;
  display: flex;
  flex-direction: row;
}
.picture-analysis { 
    flex:8;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    background-color: #fff;
    padding: 20px;
}
.video-analysis {
    background-color: #d99b9b; /* 侧边栏背景 */
    flex: 4;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 20px;
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

.controls n-button {
  background: #007bff;
  color: white;
  transition: background-color 0.3s ease;
  &:hover {
    background: #0056b3;
  }
}

.chart-container {
  width: 100%;
  height: 400px;
  border: none;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
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

.analysis-results {
  padding: 20px;
  
  .score-section {
    text-align: center;
    margin-bottom: 20px;
    
    h3 {
      margin: 0 0 10px;
      color: #333;
    }
    
    .total-score {
      font-size: 36px;
      font-weight: bold;
      color: #2080f0;
      margin: 10px 0;
    }
    
    .score-breakdown {
      display: flex;
      justify-content: space-around;
      
      .score-item {
        text-align: center;
        
        span:first-child {
          color: #666;
          margin-right: 5px;
        }
        
        span:last-child {
          font-weight: bold;
          color: #333;
        }
      }
    }
  }
}

.analysis-details {
  padding: 20px;
  
  .analysis-section {
    margin-bottom: 30px;
    
    h4 {
      margin: 0 0 15px;
      color: #333;
      border-bottom: 2px solid #eee;
      padding-bottom: 5px;
    }
    
    .detail-item {
      margin-bottom: 15px;
      
      span {
        display: block;
        margin-bottom: 5px;
        color: #666;
      }
    }
    
    .suggestions {
      background: #f5f5f5;
      padding: 15px;
      border-radius: 4px;
      color: #666;
      line-height: 1.6;
    }
  }
}

.no-results, .no-analysis {
  text-align: center;
  color: #999;
  padding: 20px;
}

.chart-container {
  height: 300px;
  margin-top: 20px;
}

.n-progress {
  .n-progress-rail {
    background-color: #e0e0e0;
  }
  .n-progress-fill {
    background-color: #2080f0;
  }
}
</style>