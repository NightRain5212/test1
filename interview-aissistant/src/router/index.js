import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ReportView from '../views/ReportView.vue'
import MyProfile from '../views/MyProfile.vue'
import HistoryView from '../views/HistoryView.vue'
import Login from '../views/Login.vue'  // 直接导入Login组件

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/report',
    name: 'report',
    component: ReportView,
    meta: { requiresAuth: true }
  },
  {
    path: '/myProfile',
    name: 'profile',
    component: MyProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: Login,  // 直接使用导入的组件
    meta: { requiresAuth: false }
  },
  {
    path: '/settings',
    name: 'settingsView',//命名，home就可以代指url路径了
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),//设置应用的基础路径为BASE_URL
  routes,
  //这里设置跳转路由后是否保存浏览位置
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})
//每个路由跳转前都会执行这个函数
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('accessToken');
  console.log('获取token',token)
  const isAuthenticated = !!token;
  
  // 如果目标路由是登录页，直接放行
  if (to.path === '/login') {
    next();
    return;
  }
  
  // 需要认证但未登录的路由
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next({ 
      path: '/login',
      query: { 
        redirect: to.fullPath,
        showLogin: 'true'
      }
    });
    return;
  }

  // 其他情况正常放行
  next();
});

export default router