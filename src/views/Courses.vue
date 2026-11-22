<template>
  <div class="page-card">
    <div class="page-head">
      <h2>课程管理 <span class="tip">共 {{ list.length }} 门课程</span></h2>
    </div>
    <el-table
      v-loading="loading"
      :data="list"
      border
      stripe
      :header-cell-style="{ background: '#f7f9fc', color: '#33415c', fontWeight: 600 }"
    >
      <el-table-column prop="cno" label="课程编号" width="120" />
      <el-table-column prop="name" label="课程名称" />
      <el-table-column prop="credit" label="学分" width="100" align="center" />
      <el-table-column prop="teacher" label="任课教师" width="140" />
      <el-table-column label="状态" width="100" align="center">
        <template #default>
          <el-tag type="success" size="small">已开课</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getCourses } from '@/api/modules'

const list = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const data = await getCourses()
    list.value = data.list
  } finally {
    loading.value = false
  }
})
</script>
