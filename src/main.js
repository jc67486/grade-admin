import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 函数式组件（ElMessage / ElMessageBox）样式需手动按需引入
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'

import App from './App.vue'
import router from './router'
import './styles.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
