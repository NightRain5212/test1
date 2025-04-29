import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',//命名，home就可以代指url路径了
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/history',
    name: 'home',
    component: () => import('../views/HistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'login',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
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
  next()//进入下一个路由
})

export default router