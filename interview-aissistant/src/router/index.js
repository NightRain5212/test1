
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'homeView',//命名，home就可以代指url路径了
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
    {
    path: '/myProfile',
    name: 'myProfileView',//命名，home就可以代指url路径了
    component: () => import('../views/MyProfile.vue'),
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
  const isAuthenticated = !!token; // 明确转换为布尔值
  
  // 情况1：访问需要认证但未登录的路由
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    return next({ 
      path: '/login',
      query: { redirect: to.fullPath } // 保存目标路由便于登录后跳转
    });
  }

  // 情况2：已登录但访问登录页（重定向到首页）
  if (isAuthenticated && to.path === '/login') {
    return next('/');
  }

  // 其他情况正常放行
  next();
});

export default router