<template>
  <div class="history-view">
    <div class="header">
      <h2>面试历史记录</h2>
      <div class="filters">
        <a-select
          v-model:value="timeRange"
          style="width: 150px"
          placeholder="选择时间范围"
        >
          <a-select-option v-for="option in timeRangeOptions" 
            :key="option.value" 
            :value="option.value"
          >
            {{ option.label }}
          </a-select-option>
        </a-select>
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索历史记录..."
          style="width: 300px"
          @search="handleSearch"
        />
      </div>
    </div>

    <div class="content">
      <a-spin :spinning="loading">
        <div v-if="records.length > 0" class="records-grid">
          <a-card v-for="record in filteredRecords" 
            :key="record.id" 
            class="record-card"
            :bordered="false"
          >
            <template #extra>
              <a-tag :color="getScoreTagColor(record.result.scores.total)">
                {{ record.result.scores.total.toFixed(1) }}分
              </a-tag>
            </template>
            <template #title>
              <span class="timestamp">{{ formatDate(record.timestamp) }}</span>
            </template>
            
            <div class="scores-container">
              <div class="score-row">
                <span class="label">视频表现</span>
                <a-progress 
                  :percent="record.result.scores.video * 100" 
                  :stroke-color="getProgressColor(record.result.scores.video)"
                />
              </div>
              <div class="score-row">
                <span class="label">语音表现</span>
                <a-progress 
                  :percent="record.result.scores.voice * 100" 
                  :stroke-color="getProgressColor(record.result.scores.voice)"
                />
              </div>
              <div class="score-row">
                <span class="label">内容表现</span>
                <a-progress 
                  :percent="record.result.scores.text * 100" 
                  :stroke-color="getProgressColor(record.result.scores.text)"
                />
              </div>
            </div>

            <div class="card-footer">
              <a-button type="link" @click="viewDetail(record)">
                查看详情
              </a-button>
              <a-button type="link" danger @click="confirmDelete(record.id)">
                删除
              </a-button>
            </div>
          </a-card>
        </div>
        <a-empty v-else description="暂无历史记录" />
      </a-spin>
    </div>

    <!-- 详情模态框 -->
    <a-modal
      v-model:visible="showDetailModal"
      title="详细分析报告"
      width="600px"
      @cancel="closeDetail"
    >
      <template v-if="selectedRecord">
        <div class="detail-content">
          <div class="detail-section">
            <h4>总体评分</h4>
            <div class="total-score">
              {{ selectedRecord.result.scores.total.toFixed(1) }}
            </div>
          </div>

          <div class="detail-section">
            <h4>详细分析</h4>
            <div class="detail-scores">
              <div class="detail-item">
                <span>姿态稳定性：</span>
                <a-progress
                  :percent="selectedRecord.result.details.video_data.posture_stability * 100"
                  :stroke-color="getProgressColor(selectedRecord.result.details.video_data.posture_stability)"
                />
              </div>
              <div class="detail-item">
                <span>手势频率：</span>
                <a-progress
                  :percent="selectedRecord.result.details.video_data.hand_movement * 100"
                  :stroke-color="getProgressColor(selectedRecord.result.details.video_data.hand_movement)"
                />
              </div>
              <div class="detail-item">
                <span>语速：</span>
                <a-progress
                  :percent="selectedRecord.result.details.voice_data.speech_rate * 20"
                  :stroke-color="getProgressColor(selectedRecord.result.details.voice_data.speech_rate / 5)"
                />
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>AI建议</h4>
            <p class="suggestions">
              {{ selectedRecord.result.suggestions }}
            </p>
          </div>
        </div>
      </template>
    </a-modal>

    <!-- 删除确认框 -->
    <a-modal
      v-model:visible="showDeleteModal"
      title="确认删除"
      :closable="false"
      @ok="handleDelete"
      @cancel="cancelDelete"
      okText="确认"
      cancelText="取消"
      okType="danger"
    >
      <p>确定要删除这条历史记录吗？此操作不可恢复。</p>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'

const loading = ref(false)
const records = ref([])
const timeRange = ref('all')
const searchText = ref('')
const showDetailModal = ref(false)
const showDeleteModal = ref(false)
const selectedRecord = ref(null)
const recordToDelete = ref(null)

const timeRangeOptions = [
  { label: '全部', value: 'all' },
  { label: '最近一周', value: 'week' },
  { label: '最近一月', value: 'month' },
  { label: '最近三月', value: 'threemonths' }
]

// 格式化日期
function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 根据分数获取进度条颜色
function getProgressColor(value) {
  if (value >= 0.8) return '#52c41a'
  if (value >= 0.6) return '#1890ff'
  if (value >= 0.4) return '#faad14'
  return '#f5222d'
}

// 根据总分获取标签颜色
function getScoreTagColor(score) {
  if (score >= 8) return 'success'
  if (score >= 6) return 'processing'
  if (score >= 4) return 'warning'
  return 'error'
}

// 过滤记录
const filteredRecords = computed(() => {
  let filtered = [...records.value]

  // 按时间范围过滤
  if (timeRange.value !== 'all') {
    const now = new Date()
    const ranges = {
      week: 7,
      month: 30,
      threemonths: 90
    }
    const days = ranges[timeRange.value]
    filtered = filtered.filter(record => {
      const recordDate = new Date(record.timestamp)
      return (now - recordDate) / (1000 * 60 * 60 * 24) <= days
    })
  }

  // 按搜索文本过滤
  if (searchText.value) {
    const searchLower = searchText.value.toLowerCase()
    filtered = filtered.filter(record => 
      record.result.suggestions.toLowerCase().includes(searchLower)
    )
  }

  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

// 获取历史记录
async function fetchRecords() {
  loading.value = true
  try {
    const userId = localStorage.getItem('userId')
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
  } finally {
    loading.value = false
  }
}

// 查看详情
function viewDetail(record) {
  selectedRecord.value = record
  showDetailModal.value = true
}

// 关闭详情
function closeDetail() {
  selectedRecord.value = null
  showDetailModal.value = false
}

// 确认删除
function confirmDelete(id) {
  recordToDelete.value = id
  showDeleteModal.value = true
}

// 取消删除
function cancelDelete() {
  recordToDelete.value = null
  showDeleteModal.value = false
}

// 执行删除
async function handleDelete() {
  try {
    // TODO: 实现删除功能
    message.success('删除成功')
    await fetchRecords() // 重新加载数据
  } catch (error) {
    message.error('删除失败')
  } finally {
    showDeleteModal.value = false
    recordToDelete.value = null
  }
}

// 搜索
function handleSearch() {
  // 搜索逻辑已通过计算属性实现
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped lang="scss">
.history-view {
  padding: 24px;
  height: 100%;
  background-color: #f4f4f9;

  .header {
    margin-bottom: 24px;

    h2 {
      margin: 0 0 16px;
      color: #333;
      font-size: 24px;
    }

    .filters {
      display: flex;
      gap: 16px;
      align-items: center;
    }
  }

  .content {
    height: calc(100% - 100px);
    overflow-y: auto;

    .records-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
      padding: 4px;
    }
  }

  .record-card {
    transition: transform 0.2s;

    &:hover {
      transform: translateY(-2px);
    }

    .timestamp {
      color: #666;
      font-size: 14px;
    }

    .scores-container {
      .score-row {
        margin-bottom: 12px;

        .label {
          display: block;
          margin-bottom: 4px;
          color: #666;
        }
      }
    }

    .card-footer {
      margin-top: 16px;
      display: flex;
      justify-content: flex-end;
      gap: 8px;
    }
  }
}

.detail-content {
  .detail-section {
    margin-bottom: 24px;

    h4 {
      margin: 0 0 16px;
      color: #333;
      font-size: 16px;
      border-bottom: 1px solid #eee;
      padding-bottom: 8px;
    }

    .total-score {
      font-size: 36px;
      font-weight: bold;
      color: #1890ff;
      text-align: center;
    }

    .detail-scores {
      .detail-item {
        margin-bottom: 16px;

        span {
          display: block;
          margin-bottom: 4px;
          color: #666;
        }
      }
    }

    .suggestions {
      color: #666;
      line-height: 1.6;
      background: #f9f9f9;
      padding: 12px;
      border-radius: 4px;
    }
  }
}
</style> 