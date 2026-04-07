import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'applications',
        name: 'Applications',
        component: () => import('@/views/applications/List.vue'),
        meta: { title: '付款申请' }
      },
      {
        path: 'applications/create',
        name: 'ApplicationCreate',
        component: () => import('@/views/applications/Create.vue'),
        meta: { title: '创建申请' }
      },
      {
        path: 'applications/:id',
        name: 'ApplicationDetail',
        component: () => import('@/views/applications/Detail.vue'),
        meta: { title: '申请详情' }
      },
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/payments/List.vue'),
        meta: { title: '付款记录' }
      },
      {
        path: 'comparison',
        name: 'Comparison',
        component: () => import('@/views/comparison/List.vue'),
        meta: { title: '对比结果' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Reports.vue'),
        meta: { title: '报表统计' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    document.title = `${to.meta.title || '财务付款对比系统'} - 财务付款对比系统`
    next()
  }
})

export default router