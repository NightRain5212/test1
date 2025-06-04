<template>
  <!-- vue提供组件---将模态框渲染到 body 末尾 -->
  <Teleport to="#modal-root">
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
import { setAddModal } from './index.js';
// 在 setup 中设置 addModal

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
setAddModal(addModal);
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
// 暴露给外部调用
defineExpose({ addModal });
</script>
<style scoped lang="scss"> 
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
</style>