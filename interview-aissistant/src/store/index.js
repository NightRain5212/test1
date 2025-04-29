import { defineStore } from 'pinia';

export const useStore = defineStore('alerts', {
  state: () => ({
    islogin: false, // 是否处于登录状态
  }),//响应式对象
  getters: {
    isLogin: (state) => state.islogin,
  },
  actions: {
    login() {
      this.islogin = true; // 更新登录状态
    },
    logout() {
      this.islogin = false; // 更新为未登录状态
    },
  },
});
