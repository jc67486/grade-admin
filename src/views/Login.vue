<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="login-card__head">
        <h1>学生成绩管理系统</h1>
        <p>Student Grade Management System</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="submit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="密码" :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="submit">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-tip">
        演示账号：<b>teacher</b> / 123456（教师）　<b>student</b> / 123456（学生）
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/modules'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const store = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: 'teacher', password: '123456' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码不少于 6 位', trigger: 'blur' }
  ]
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const data = await login({ ...form })
    store.setLogin(data)
    ElMessage.success(`欢迎回来，${data.user.name}`)
    const redirect = route.query.redirect ? decodeURIComponent(route.query.redirect) : '/students'
    router.replace(redirect)
  } finally {
    loading.value = false
  }
}

/* 开发/演示自动登录：/?auto=teacher 时直接用演示账号进入 */
onMounted(async () => {
  const auto = new URLSearchParams(location.search).get('auto')
  if (auto && !store.isLogin) {
    form.username = auto
    await submit()
  }
})
</script>

<style scoped>
.login-wrap {
  height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #1f2a44 0%, #2f5bff 55%, #4b7bff 100%);
}
.login-card {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 34px 34px 24px;
  box-shadow: 0 18px 50px rgba(15, 30, 70, 0.28);
}
.login-card__head { text-align: center; margin-bottom: 22px; }
.login-card__head h1 { margin: 0; font-size: 22px; color: #1f2d3d; letter-spacing: 1px; }
.login-card__head p { margin: 6px 0 0; font-size: 12px; color: #9aa5b8; letter-spacing: 0.5px; }
.login-tip { text-align: center; font-size: 12px; color: #8a94a6; margin-top: 4px; line-height: 1.8; }
</style>
