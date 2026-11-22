<template>
  <div>
    <div class="page-card" style="margin-bottom: 16px">
      <div class="page-head">
        <h2>成绩录入</h2>
        <span class="tip">录入前请确认学生与课程，重复录入会被拦截</span>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" inline label-width="72px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="form.student_id" filterable placeholder="搜索学生" style="width: 200px">
            <el-option
              v-for="s in students"
              :key="s.id"
              :label="`${s.sno} ${s.name}`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="form.course_id" placeholder="选择课程" style="width: 190px">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="成绩" prop="score">
          <el-input-number v-model="form.score" :min="0" :max="100" :precision="1" style="width: 140px" />
        </el-form-item>
        <el-form-item label="学期" prop="term">
          <el-select v-model="form.term" style="width: 150px">
            <el-option label="2024-2025-1" value="2024-2025-1" />
            <el-option label="2024-2025-2" value="2024-2025-2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit">提交成绩</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card">
      <div class="page-head">
        <h2>成绩明细 <span class="tip">共 {{ filtered.length }} 条</span></h2>
      </div>
      <div class="toolbar">
        <el-input
          v-model="keyword"
          placeholder="按姓名或学号筛选"
          clearable
          style="width: 220px"
          :prefix-icon="Search"
        />
        <el-select v-model="courseId" placeholder="全部课程" clearable style="width: 180px">
          <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </div>
      <el-table
        v-loading="loading"
        :data="filtered"
        border
        stripe
        max-height="420"
        :header-cell-style="{ background: '#f7f9fc', color: '#33415c', fontWeight: 600 }"
      >
        <el-table-column prop="sno" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="class_name" label="班级" width="130" />
        <el-table-column prop="course" label="课程" />
        <el-table-column prop="credit" label="学分" width="80" align="center" />
        <el-table-column prop="score" label="成绩" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="tagType(row.score)" effect="light">{{ row.score }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="term" label="学期" width="130" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElTag } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getStudents, getCourses, getGrades, createGrade } from '@/api/modules'
import { useUserStore } from '@/store/user'

const store = useUserStore()
const students = ref([])
const courses = ref([])
const grades = ref([])
const loading = ref(false)
const submitting = ref(false)
const keyword = ref('')
const courseId = ref('')

const formRef = ref()
const form = reactive({ student_id: null, course_id: null, score: 85, term: '2024-2025-1' })
const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  score: [
    { required: true, message: '请输入成绩', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: '成绩需在 0–100 之间', trigger: 'blur' }
  ]
}

const filtered = computed(() =>
  grades.value.filter((g) =>
    (!courseId.value || g.course === courses.value.find((c) => c.id === courseId.value)?.name) &&
    (!keyword.value || g.name.includes(keyword.value) || g.sno.includes(keyword.value))
  )
)

function tagType(score) {
  if (score >= 90) return 'success'
  if (score >= 60) return 'primary'
  return 'danger'
}

async function loadAll() {
  loading.value = true
  try {
    const [s, c, g] = await Promise.all([getStudents({ page: 1, size: 100 }), getCourses(), getGrades({})])
    students.value = s.list
    courses.value = c.list
    grades.value = g.list
  } finally {
    loading.value = false
  }
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await createGrade({ ...form })
    ElMessage.success('成绩录入成功')
    formRef.value.resetFields(['student_id', 'course_id'])
    loadAll()
  } finally {
    submitting.value = false
  }
}

function reset() {
  formRef.value.resetFields()
}

onMounted(loadAll)
</script>
