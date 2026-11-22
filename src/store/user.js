import { defineStore } from 'pinia'

const KEY = 'ga_user'

function readCache() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || 'null')
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => {
    const cache = readCache() || {}
    return {
      token: cache.token || '',
      user: cache.user || null,
      /** 路由表过滤后的菜单 */
      menus: []
    }
  },
  getters: {
    isLogin: (s) => !!s.token,
    role: (s) => s.user?.role || '',
    isTeacher: (s) => s.user?.role === 'teacher'
  },
  actions: {
    setLogin({ token, user }) {
      this.token = token
      this.user = user
      localStorage.setItem(KEY, JSON.stringify({ token, user }))
    },
    logout() {
      this.token = ''
      this.user = null
      this.menus = []
      localStorage.removeItem(KEY)
    }
  }
})
