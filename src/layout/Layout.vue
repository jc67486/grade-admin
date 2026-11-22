<template>
  <el-container class="layout">
    <el-aside width="208px" class="aside">
      <div class="brand">
        <el-icon><School /></el-icon>
        <span>成绩管理系统</span>
      </div>
      <el-menu :default-active="route.path" router class="menu">
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          <el-icon><component :is="ICONS[m.icon]" /></el-icon>
          <span>{{ m.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="crumb">
          <el-icon><Location /></el-icon>
          <span>{{ route.meta.title || '首页' }}</span>
          <el-tag size="small" type="info" effect="plain" style="margin-left: 10px">
            {{ store.isTeacher ? '教师' : '学生' }}账号
          </el-tag>
        </div>
        <el-dropdown @command="onCommand">
          <span class="user">
            <el-avatar :size="28">{{ (store.user?.name || '?').slice(0, 1) }}</el-avatar>
            <span class="user__name">{{ store.user?.name }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  School, Location, ArrowDown,
  User, Reading, EditPen, DataLine, UserFilled
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { buildMenus } from '@/router'

/** 菜单图标映射：按需引入后不再全局注册图标组件 */
const ICONS = { User, Reading, EditPen, DataLine, UserFilled }

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const menus = computed(() => buildMenus(store.role))

async function onCommand(cmd) {
  if (cmd === 'profile') return router.push('/profile')
  await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { height: 100vh; }
.aside {
  background: #1f2a44;
  color: #fff;
  display: flex;
  flex-direction: column;
}
.brand {
  height: 58px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 18px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.menu {
  border-right: 0;
  background: transparent;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: #b9c4d8;
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.07);
  --el-menu-active-color: #fff;
}
:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #2f5bff, #4b7bff);
}
.header {
  height: 58px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eef1f6;
}
.crumb { display: flex; align-items: center; gap: 6px; color: #4a5568; }
.user { display: flex; align-items: center; gap: 8px; cursor: pointer; outline: none; }
.user__name { font-size: 14px; color: #33415c; }
.main { padding: 16px; background: #f4f6fa; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.16s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
