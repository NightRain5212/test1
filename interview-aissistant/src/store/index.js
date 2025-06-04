// store/auth.js
import { defineStore } from 'pinia';

export const useStore = defineStore('auth', {
  state: () => ({
    isLoggedIn: false, // 表示用户是否处于登录状态
    userInfo: {
      username: '', // 用户名
      email: '', // 用户邮箱
      avatarSrc: '',// 用户头像的URL
      bio: '', // 用户简介''
    },
  }),
  actions: {
    login() {
      this.isLoggedIn = true; // 设置为已登录
    },
    logout() {
      this.isLoggedIn = false; // 设置为未登录
    },
    getUser(){
      return this.userInfo;
    },
    save(userInfo){
      this.userInfo.username = userInfo.username;
      this.userInfo.email = userInfo.email;
      //this.userInfo.avatarSrc = userInfo.avatarSrc;
      this.userInfo.bio = userInfo.preference?.bio??'';
    }
  },
});
