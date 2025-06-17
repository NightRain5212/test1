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
    //用于临时存储，防止数据丢失
    userTempFiles: {
      images: [] ,   // 图片文件，如图表，用户头像等，格式:{name:'',data:''}
      audios: [] ,   // 当前正在进行的音频文件,格式:{name:'',data:''}
      videos: [] ,    // 当前正在进行的视频文件格式:{name:'',data:''}
      documents: []  // 报告,格式:{name:'',data:''}
    },
    userHistory:[]//一个列表,每项包括评分、资源的url地址等。
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
    setUser(userInfo){
      this.userInfo.username = userInfo.username;
      this.userInfo.email = userInfo.email;

      this.userInfo.avatarSrc = userInfo.preference?.avatarSrc??'';
      this.userInfo.bio = userInfo.preference?.bio??'';
    },
    // 文件操作方法
    saveFiles(files) {
      files.forEach(file => {
        const type = this._getFileType(file.name);
        this.userFiles[type].push(file);
      });
    },
    clearFiles() {
      this.userFiles = {
        images: [],
        audios: [],
        videos: [],
        documents: []
      };
    },
    // 私有方法 - 根据文件名判断文件类型
    _getFileType(filename) {
      const extension = filename.split('.').pop().toLowerCase();
      const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
      const audioTypes = ['mp3', 'wav', 'ogg'];
      const videoTypes = ['mp4', 'webm', 'mov'];
      
      if (imageTypes.includes(extension)) return 'images';
      if (audioTypes.includes(extension)) return 'audios';
      if (videoTypes.includes(extension)) return 'videos';
      return 'documents';
    }
  },
});
