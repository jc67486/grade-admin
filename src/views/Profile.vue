<template>
  <div class="page-card" style="max-width: 640px">
    <div class="page-head"><h2>个人中心</h2></div>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="用户名">{{ store.user?.username }}</el-descriptions-item>
      <el-descriptions-item label="姓名">{{ store.user?.name }}</el-descriptions-item>
      <el-descriptions-item label="角色">
        <el-tag :type="store.isTeacher ? 'success' : 'info'" size="small">
          {{ store.isTeacher ? '教师' : '学生' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="可访问菜单">
        <el-tag v-for="m in menus" :key="m.path" size="small" style="margin-right: 6px">
          {{ m.title }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="登录态">
        token 存于 Pinia + localStorage，刷新不丢失
      </el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElTag } from 'element-plus'
import { useUserStore } from '@/store/user'
import { buildMenus } from '@/router'

const store = useUserStore()
const menus = computed(() => buildMenus(store.role))
</script>
