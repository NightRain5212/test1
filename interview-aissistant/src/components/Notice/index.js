import Notice from './Notice.vue';

// 定义一个变量来保存 addModal 函数
let _addModal = null;

// 包装一个函数，在组件加载完成后调用 addModal
function addModal(modalConfig) {
  if (_addModal) {
    _addModal(modalConfig);
  } else {
    // 如果组件还没挂载，就缓存请求
    setTimeout(() => {
      if (_addModal) {
        _addModal(modalConfig);
      } else {
        console.warn('Notice 组件尚未加载完成');
      }
    }, 10);
  }
}

export { Notice, addModal };

// 这个函数会在组件被挂载后设置真正的 addModal 方法
export function setAddModal(fn) {
  _addModal = fn;
}