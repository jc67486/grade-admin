import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

/** 路由表：meta.roles 为空表示登录即可访问 */
export const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layout/Layout.vue'),
    redirect: '/students',
    children: [
      {
        path: 'students',
        name: 'students',
        component: () => import('@/views/Students.vue'),
        meta: { title: '学生管理', icon: 'User', roles: ['teacher'] }
      },
      {
        path: 'courses',
        name: 'courses',
        component: () => import('@/views/Courses.vue'),
        meta: { title: '课程管理', icon: 'Reading' }
      },
      {
        path: 'grades',
        name: 'grades',
        component: () => import('@/views/Grades.vue'),
        meta: { title: '成绩管理', icon: 'EditPen' }
      },
      {
        path: 'stats',
        name: 'stats',
        component: () => import('@/views/Stats.vue'),
        meta: { title: '成绩统计', icon: 'DataLine' }
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', icon: 'UserFilled' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'notFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { public: true, title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

/** 按角色过滤路由表，生成动态菜单 */
export function buildMenus(role) {
  const parent = routes.find((r) => r.path === '/')
  return parent.children
    .filter((c) => !c.meta?.roles || c.meta.roles.includes(role))
    .map((c) => ({ path: '/' + c.path, title: c.meta.title, icon: c.meta.icon }))
}

router.beforeEach((to) => {
  const store = useUserStore()
  const title = to.meta?.title ? `${to.meta.title} · 学生成绩管理系统` : '学生成绩管理系统'
  document.title = title

  if (to.meta?.public) {
    // 已登录访问登录页 -> 回首页
    if (to.name === 'login' && store.isLogin) return { path: '/students' }
    return true
  }

  // 未登录：记录 redirect，跳登录
  if (!store.isLogin) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // 角色无权：回到第一个可访问页面
  const roles = to.meta?.roles
  if (roles && !roles.includes(store.role)) {
    const first = buildMenus(store.role)[0]
    return first ? { path: first.path } : { path: '/profile' }
  }
  return true
})

export default router
