<template>
  <div class="history-container">
    <h2>历史记录</h2>
    <div v-if="records.length > 0" class="history-list">
      <div v-for="record in records" :key="record.id" class="history-item">
        <div class="history-header">
          <span class="timestamp">{{ formatDate(record.timestamp) }}</span>
          <span class="action">{{ record.action }}</span>
        </div>
        <div class="history-content">
          <div class="scores">
            <div class="score-item">
              <span>视频表现：</span>
              <span>{{ record.result.scores.video.toFixed(2) }}</span>
            </div>
            <div class="score-item">
              <span>语音表现：</span>
              <span>{{ record.result.scores.voice.toFixed(2) }}</span>
            </div>
            <div class="score-item">
              <span>内容表现：</span>
              <span>{{ record.result.scores.text.toFixed(2) }}</span>
            </div>
          </div>
          <div class="total-score">
            总分：{{ record.result.scores.total.toFixed(2) }}
          </div>
        </div>
      </div>
    </div>
    <div v-else class="no-records">
      暂无历史记录
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'

const records = ref([])

// 格式化日期
function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取历史记录
async function fetchHistory() {
  try {
    const userId = localStorage.getItem('userId') // 从localStorage获取用户ID
    if (!userId) {
      message.error('请先登录')
      return
    }

    const response = await fetch(`http://localhost:8000/api/history?user_id=${userId}`)
    if (!response.ok) {
      throw new Error('获取历史记录失败')
    }

    const data = await response.json()
    records.value = data.data
  } catch (error) {
    console.error('获取历史记录失败:', error)
    message.error('获取历史记录失败')
  }
}

// 组件挂载时获取历史记录
onMounted(() => {
  fetchHistory()
})
</script>

<style scoped lang="scss">
.history-container {
  padding: 20px;
  
  h2 {
    margin-bottom: 20px;
    color: #333;
  }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .history-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;

    .timestamp {
      color: #666;
      font-size: 14px;
    }

    .action {
      color: #1890ff;
      font-weight: 500;
    }
  }

  .history-content {
    .scores {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-bottom: 12px;

      .score-item {
        span:first-child {
          color: #666;
          margin-right: 8px;
        }

        span:last-child {
          color: #333;
          font-weight: 500;
        }
      }
    }

    .total-score {
      text-align: right;
      color: #1890ff;
      font-size: 16px;
      font-weight: bold;
    }
  }
}

.no-records {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
</style> 