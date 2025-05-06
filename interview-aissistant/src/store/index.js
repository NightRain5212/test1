// store/auth.js
import { defineStore } from 'pinia';

export const useStore = defineStore('auth', {
  state: () => ({
    isLoggedIn: false, // 表示用户是否处于登录状态
  }),
  actions: {
    login() {
      this.isLoggedIn = true; // 设置为已登录
    },
    logout() {
      this.isLoggedIn = false; // 设置为未登录
    },
  },
});
