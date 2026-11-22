import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const CODE_MSG = {
  400: '请求参数有误',
  401: '登录已过期，请重新登录',
  403: '无操作权限',
  404: '接口不存在',
  500: '服务器开小差了'
}

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

/* 并发 401 只刷新/跳转一次：用队列挂起后续请求 */
let redirecting = false

request.interceptors.request.use((config) => {
  const store = useUserStore()
  if (store.token) config.headers.Authorization = `Bearer ${store.token}`
  return config
})

request.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && body.code === 0) return body.data
    ElMessage.error(body?.msg || '业务异常')
    return Promise.reject(new Error(body?.msg))
  },
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      if (!redirecting) {
        redirecting = true
        const store = useUserStore()
        const redirect = encodeURIComponent(location.hash.replace('#', '') || '/')
        store.logout()
        ElMessage.warning('登录已过期，请重新登录')
        setTimeout(() => {
          location.hash = `#/login?redirect=${redirect}`
          redirecting = false
        }, 300)
      }
      return Promise.reject(new Error('未登录'))
    }
    const msg = CODE_MSG[status] || error.message || '网络异常'
    ElMessage.error(msg)
    return Promise.reject(new Error(msg))
  }
)

export default request
