<template>
  <div class="post-detail-container">
    <!-- 帖子内容 -->
    <a-card v-if="post" class="post-content">
      <div class="post-header">
        <h2>{{ post.title }}</h2>
        <div class="post-meta">
          <a-tag>{{ post.post_type }}</a-tag>
          <span class="post-author">作者：{{ post.username }}</span>
          <span class="post-time">发布时间：{{ formatDate(post.created_at) }}</span>
        </div>
        <div class="post-tags" v-if="post.tags">
          <a-tag
            v-for="tag in post.tags.split(',')"
            :key="tag"
            color="blue"
          >
            {{ tag }}
          </a-tag>
        </div>
      </div>
      
      <div class="post-body">
        {{ post.content }}
      </div>
      
      <div class="post-stats">
        <span><EyeOutlined /> {{ post.views }} 浏览</span>
        <span @click="likePost" class="like-btn">
          <StarOutlined /> {{ post.likes }} 点赞
        </span>
      </div>
    </a-card>

    <!-- 评论区 -->
    <a-card class="comments-section">
      <template #title>
        评论 ({{ comments.length }})
      </template>
      
      <!-- 发表评论 -->
      <div class="comment-form">
        <a-textarea
          v-model:value="newComment"
          :rows="3"
          placeholder="写下你的评论..."
        />
        <a-button
          type="primary"
          @click="submitComment"
          :disabled="!newComment.trim()"
          class="submit-btn"
        >
          发表评论
        </a-button>
      </div>

      <!-- 评论列表 -->
      <a-list
        class="comment-list"
        :data-source="comments"
        item-layout="horizontal"
      >
        <template #renderItem="{ item: comment }">
          <a-list-item>
            <div class="comment-item">
              <div class="comment-header">
                <span class="comment-author">{{ comment.username }}</span>
                <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              </div>
              <div class="comment-content">
                {{ comment.content }}
              </div>
              <div class="comment-footer">
                <span @click="likeComment(comment.id)" class="like-btn">
                  <StarOutlined /> {{ comment.likes }} 点赞
                </span>
              </div>
            </div>
          </a-list-item>
        </template>
      </a-list>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  EyeOutlined,
  StarOutlined
} from '@ant-design/icons-vue'
import axios from '../utils/axios'

const route = useRoute()
const postId = route.params.id

const post = ref(null)
const comments = ref([])
const newComment = ref('')

// 获取帖子详情
const fetchPostDetail = async () => {
  try {
    const response = await axios.get(`/api/community/posts/${postId}`)
    post.value = response.data.data.post
    comments.value = response.data.data.comments
  } catch (error) {
    message.error('获取帖子详情失败')
  }
}

// 提交评论
const submitComment = async () => {
  try {
    await axios.post('/api/community/comments', {
      post_id: postId,
      content: newComment.value
    })
    message.success('评论成功')
    newComment.value = ''
    fetchPostDetail()
  } catch (error) {
    message.error('评论失败')
  }
}

// 点赞帖子
const likePost = async () => {
  try {
    await axios.post(`/api/community/posts/${postId}/like`)
    post.value.likes++
    message.success('点赞成功')
  } catch (error) {
    message.error('点赞失败')
  }
}

// 点赞评论
const likeComment = async (commentId) => {
  try {
    await axios.post(`/api/community/comments/${commentId}/like`)
    const comment = comments.value.find(c => c.id === commentId)
    if (comment) {
      comment.likes++
    }
    message.success('点赞成功')
  } catch (error) {
    message.error('点赞失败')
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleString()
}

onMounted(() => {
  fetchPostDetail()
})
</script>

<style scoped lang="scss">
.post-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;

  .post-content {
    margin-bottom: 20px;

    .post-header {
      margin-bottom: 20px;

      h2 {
        margin: 0 0 10px 0;
      }

      .post-meta {
        margin: 10px 0;
        color: rgba(0, 0, 0, 0.45);
        font-size: 14px;

        span {
          margin-right: 15px;
        }
      }

      .post-tags {
        margin-top: 10px;

        .ant-tag {
          margin-right: 8px;
        }
      }
    }

    .post-body {
      font-size: 16px;
      line-height: 1.6;
      margin-bottom: 20px;
    }

    .post-stats {
      color: rgba(0, 0, 0, 0.45);
      font-size: 14px;

      span {
        margin-right: 20px;
        cursor: pointer;

        .anticon {
          margin-right: 4px;
        }
      }

      .like-btn {
        &:hover {
          color: #1890ff;
        }
      }
    }
  }

  .comments-section {
    .comment-form {
      margin-bottom: 24px;

      .submit-btn {
        margin-top: 16px;
        float: right;
      }
    }

    .comment-list {
      .comment-item {
        width: 100%;

        .comment-header {
          margin-bottom: 8px;

          .comment-author {
            font-weight: bold;
            margin-right: 10px;
          }

          .comment-time {
            color: rgba(0, 0, 0, 0.45);
            font-size: 12px;
          }
        }

        .comment-content {
          font-size: 14px;
          line-height: 1.6;
          margin-bottom: 8px;
        }

        .comment-footer {
          .like-btn {
            color: rgba(0, 0, 0, 0.45);
            font-size: 12px;
            cursor: pointer;

            &:hover {
              color: #1890ff;
            }

            .anticon {
              margin-right: 4px;
            }
          }
        }
      }
    }
  }
}
</style> 