import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',//命名，home就可以代指url路径了
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
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
  if(!localStorage.getItem('token')){
    if(to.meta.requiresAuth){//如果需要验证登录状态，并且没有token，那么就跳转到登录页面
      next('/login')
    }
  }
  next()//进入下一个路由
})

export default router