<template>
  <div class="community-container">
    <!-- 顶部导航 -->
    <a-tabs v-model:activeKey="currentTab" class="nav-tabs">
      <a-tab-pane v-for="tab in tabs" :key="tab.type" :tab="tab.name" />
    </a-tabs>

    <!-- 帖子列表 -->
    <div v-if="currentTab === 'posts'" class="posts-section">
      <!-- 筛选器 -->
      <div class="filters">
        <a-select
          v-model:value="postType"
          placeholder="选择帖子类型"
          allowClear
          style="width: 200px"
        >
          <a-select-option
            v-for="type in postTypes"
            :key="type.value"
            :value="type.value"
          >
            {{ type.label }}
          </a-select-option>
        </a-select>
        <a-input
          v-model:value="searchTags"
          placeholder="输入标签搜索"
          allowClear
          class="tag-input"
        />
        <a-button type="primary" @click="createPost">发布帖子</a-button>
      </div>

      <!-- 帖子列表 -->
      <div class="post-list">
        <a-card v-for="post in posts" :key="post.id" class="post-item" hoverable @click="viewPost(post.id)">
          <div class="post-header">
            <a-tag>{{ post.post_type }}</a-tag>
            <h3 class="post-title">{{ post.title }}</h3>
          </div>
          <div class="post-content">{{ post.content }}</div>
          <div class="post-footer">
            <div class="post-info">
              <span>{{ post.username }}</span>
              <span>{{ formatDate(post.created_at) }}</span>
            </div>
            <div class="post-stats">
              <span><EyeOutlined /> {{ post.views }}</span>
              <span><CommentOutlined /> {{ post.comment_count }}</span>
              <span><StarOutlined /> {{ post.likes }}</span>
            </div>
          </div>
        </a-card>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <a-pagination
          v-model:current="page"
          :total="total"
          :pageSize="pageSize"
          @change="handlePageChange"
        />
      </div>
    </div>

    <!-- 资源推荐 -->
    <div v-if="currentTab === 'resources'" class="resources-section">
      <div class="filters">
        <a-select
          v-model:value="resourceCategory"
          placeholder="选择资源类别"
          allowClear
          style="width: 200px"
        >
          <a-select-option
            v-for="category in resourceCategories"
            :key="category.value"
            :value="category.value"
          >
            {{ category.label }}
          </a-select-option>
        </a-select>
        <a-button type="primary" @click="createResource">添加资源</a-button>
      </div>

      <div class="resource-list">
        <a-card v-for="resource in resources" :key="resource.id" class="resource-item" hoverable>
          <div class="resource-title">
            <h3>{{ resource.title }}</h3>
            <a-tag>{{ resource.category }}</a-tag>
          </div>
          <div class="resource-description">{{ resource.description }}</div>
          <div class="resource-footer">
            <a-button type="link" @click="visitResource(resource)">访问链接</a-button>
            <span class="click-count">点击次数: {{ resource.clicks }}</span>
          </div>
        </a-card>
      </div>
    </div>

    <!-- 发帖对话框 -->
    <a-modal
      v-model:visible="postDialogVisible"
      title="发布帖子"
      @ok="submitPost"
      @cancel="postDialogVisible = false"
      okText="发布"
      cancelText="取消"
    >
      <a-form :model="newPost" layout="vertical">
        <a-form-item label="标题">
          <a-input v-model:value="newPost.title" />
        </a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="newPost.post_type">
            <a-select-option
              v-for="type in postTypes"
              :key="type.value"
              :value="type.value"
            >
              {{ type.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="标签">
          <a-input v-model:value="newPost.tags" placeholder="多个标签用逗号分隔" />
        </a-form-item>
        <a-form-item label="内容">
          <a-textarea
            v-model:value="newPost.content"
            :rows="6"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 添加资源对话框 -->
    <a-modal
      v-model:visible="resourceDialogVisible"
      title="添加资源"
      @ok="submitResource"
      @cancel="resourceDialogVisible = false"
      okText="添加"
      cancelText="取消"
    >
      <a-form :model="newResource" layout="vertical">
        <a-form-item label="标题">
          <a-input v-model:value="newResource.title" />
        </a-form-item>
        <a-form-item label="链接">
          <a-input v-model:value="newResource.url" />
        </a-form-item>
        <a-form-item label="类别">
          <a-select v-model:value="newResource.category">
            <a-select-option
              v-for="category in resourceCategories"
              :key="category.value"
              :value="category.value"
            >
              {{ category.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="标签">
          <a-input v-model:value="newResource.tags" placeholder="多个标签用逗号分隔" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea
            v-model:value="newResource.description"
            :rows="4"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  EyeOutlined,
  CommentOutlined,
  StarOutlined
} from '@ant-design/icons-vue'
import axios from '../utils/axios'

const router = useRouter()

// 状态变量
const currentTab = ref('posts')
const postType = ref('')
const searchTags = ref('')
const resourceCategory = ref('')
const posts = ref([])
const resources = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const postDialogVisible = ref(false)
const resourceDialogVisible = ref(false)

// 新帖子和新资源的表单数据
const newPost = ref({
  title: '',
  post_type: '',
  tags: '',
  content: ''
})

const newResource = ref({
  title: '',
  url: '',
  category: '',
  tags: '',
  description: ''
})

// 常量数据
const tabs = [
  { type: 'posts', name: '讨论区' },
  { type: 'resources', name: '资源推荐' }
]

const postTypes = [
  { value: '面试题', label: '面试题' },
  { value: '实时面试', label: '实时面试' },
  { value: '经验分享', label: '经验分享' },
  { value: '资源分享', label: '资源分享' }
]

const resourceCategories = [
  { value: '面试题库', label: '面试题库' },
  { value: '学习资源', label: '学习资源' },
  { value: '求职网站', label: '求职网站' },
  { value: '技术博客', label: '技术博客' }
]

// 方法
const fetchPosts = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      post_type: postType.value,
      tags: searchTags.value
    }
    const response = await axios.get('/api/community/posts', { params })
    posts.value = response.data.data.posts
    total.value = response.data.data.total
  } catch (error) {
    message.error('获取帖子列表失败')
  }
}

const fetchResources = async () => {
  try {
    const params = {
      category: resourceCategory.value
    }
    const response = await axios.get('/api/community/resources', { params })
    resources.value = response.data.data.resources
  } catch (error) {
    message.error('获取资源列表失败')
  }
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchPosts()
}

const createPost = () => {
  postDialogVisible.value = true
}

const createResource = () => {
  resourceDialogVisible.value = true
}

const submitPost = async () => {
  try {
    await axios.post('/api/community/posts', newPost.value)
    message.success('发布成功')
    postDialogVisible.value = false
    fetchPosts()
  } catch (error) {
    message.error('发布失败')
  }
}

const submitResource = async () => {
  try {
    await axios.post('/api/community/resources', newResource.value)
    message.success('添加成功')
    resourceDialogVisible.value = false
    fetchResources()
  } catch (error) {
    message.error('添加失败')
  }
}

const viewPost = (postId) => {
  router.push(`/community/post/${postId}`)
}

const visitResource = async (resource) => {
  try {
    await axios.post(`/api/community/resources/${resource.id}/click`)
    window.open(resource.url, '_blank')
  } catch (error) {
    message.error('访问失败')
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleString()
}

// 生命周期钩子
onMounted(() => {
  fetchPosts()
})
</script>

<style scoped lang="scss">
.community-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 64px);
  background-color: #f5f5f5;

  .nav-tabs {
    background: #fff;
    padding: 0 24px;
    margin-bottom: 24px;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);

    :deep(.ant-tabs-nav) {
      margin-bottom: 0;
    }

    :deep(.ant-tabs-tab) {
      padding: 16px 0;
      font-size: 16px;
      margin: 0 24px 0 0;
    }
  }

  .filters {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    align-items: center;
    background: #fff;
    padding: 16px 24px;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);

    .tag-input {
      width: 200px;
    }

    .ant-btn {
      margin-left: auto;
    }
  }

  .post-list {
    .post-item {
      margin-bottom: 16px;
      cursor: pointer;
      border-radius: 8px;
      overflow: hidden;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      }

      :deep(.ant-card-body) {
        padding: 20px 24px;
      }

      .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;

        .ant-tag {
          margin-right: 12px;
          font-size: 12px;
          padding: 2px 8px;
          border-radius: 4px;
          background: #e6f7ff;
          color: #1890ff;
          border: none;
        }

        .post-title {
          margin: 0;
          font-size: 18px;
          font-weight: 500;
          color: #262626;
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .post-content {
        color: rgba(0, 0, 0, 0.65);
        margin-bottom: 16px;
        font-size: 14px;
        line-height: 1.6;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }

      .post-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        color: rgba(0, 0, 0, 0.45);

        .post-info {
          display: flex;
          align-items: center;

          span {
            margin-right: 16px;
            display: flex;
            align-items: center;

            &:last-child {
              margin-right: 0;
            }
          }
        }

        .post-stats {
          display: flex;
          align-items: center;

          span {
            display: flex;
            align-items: center;
            margin-left: 20px;
            transition: color 0.3s ease;

            &:hover {
              color: #1890ff;
            }

            .anticon {
              margin-right: 6px;
              font-size: 16px;
            }
          }
        }
      }
    }
  }

  .resources-section {
    .resource-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
      margin-top: 8px;

      .resource-item {
        height: 100%;
        border-radius: 8px;
        overflow: hidden;
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        :deep(.ant-card-body) {
          padding: 20px;
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .resource-title {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;

          h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
            color: #262626;
            flex: 1;
            padding-right: 12px;
          }

          .ant-tag {
            flex-shrink: 0;
            background: #f6ffed;
            color: #52c41a;
            border: none;
          }
        }

        .resource-description {
          color: rgba(0, 0, 0, 0.65);
          margin-bottom: 16px;
          font-size: 14px;
          line-height: 1.6;
          flex: 1;
        }

        .resource-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: auto;

          .ant-btn {
            padding: 0;
            height: auto;
            font-size: 14px;
          }

          .click-count {
            font-size: 13px;
            color: rgba(0, 0, 0, 0.45);
          }
        }
      }
    }
  }

  .pagination {
    margin-top: 24px;
    text-align: center;
    background: #fff;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  }
}

// 对话框样式美化
:deep(.ant-modal) {
  .ant-modal-content {
    border-radius: 8px;
    overflow: hidden;
  }

  .ant-modal-header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;

    .ant-modal-title {
      font-size: 18px;
      font-weight: 500;
    }
  }

  .ant-modal-body {
    padding: 24px;

    .ant-form-item {
      margin-bottom: 24px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .ant-input,
    .ant-select {
      border-radius: 4px;
    }

    textarea.ant-input {
      resize: vertical;
      min-height: 120px;
    }
  }

  .ant-modal-footer {
    padding: 16px 24px;
    border-top: 1px solid #f0f0f0;

    .ant-btn {
      border-radius: 4px;
      height: 36px;
      padding: 0 20px;

      & + .ant-btn {
        margin-left: 12px;
      }
    }
  }
}
</style>