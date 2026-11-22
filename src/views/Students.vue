<template>
  <div class="page-card">
    <div class="page-head">
      <h2>学生管理 <span class="tip">共 {{ total }} 名学生</span></h2>
      <el-button type="primary" :icon="Plus" @click="openDialog()">新增学生</el-button>
    </div>

    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="按姓名或学号搜索"
        clearable
        style="width: 220px"
        :prefix-icon="Search"
        @keyup.enter="search"
        @clear="search"
      />
      <el-select v-model="query.class" placeholder="全部班级" clearable style="width: 150px" @change="search">
        <el-option v-for="c in classes" :key="c" :label="c" :value="c" />
      </el-select>
      <el-button type="primary" plain @click="search">查询</el-button>
      <el-button @click="reset">重置</el-button>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated style="padding: 12px 4px" />
    <el-table
      v-else
      :data="list"
      border
      stripe
      style="width: 100%"
      :header-cell-style="{ background: '#f7f9fc', color: '#33415c', fontWeight: 600 }"
      empty-text="暂无数据"
    >
      <el-table-column type="index" label="#" width="56" align="center" />
      <el-table-column prop="sno" label="学号" width="120" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="gender" label="性别" width="70" align="center" />
      <el-table-column prop="class_name" label="班级" width="130" />
      <el-table-column prop="phone" label="联系电话" width="140" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="load"
      />
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑学生' : '新增学生'" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="76px">
        <el-form-item label="学号" prop="sno">
          <el-input v-model="form.sno" :disabled="!!dialog.id" placeholder="8 位数字" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="班级" prop="class_name">
          <el-select v-model="form.class_name" style="width: 100%">
            <el-option v-for="c in classes" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="11 位手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="dialog.loading" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getStudents, createStudent, updateStudent, removeStudent } from '@/api/modules'

const classes = ['大数据2301', '大数据2302', '软件2301', '软件2302']
const list = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, size: 10, keyword: '', class: '' })

const formRef = ref()
const dialog = reactive({ visible: false, loading: false, id: null })
const form = reactive({ sno: '', name: '', gender: '男', class_name: '大数据2301', phone: '' })

const rules = {
  sno: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^\d{8}$/, message: '学号必须为 8 位数字', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  class_name: [{ required: true, message: '请选择班级', trigger: 'change' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }]
}

async function load() {
  loading.value = true
  try {
    const data = await getStudents({
      page: query.page, size: query.size,
      keyword: query.keyword, class: query.class
    })
    list.value = data.list
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function search() {
  query.page = 1
  load()
}

function reset() {
  query.keyword = ''
  query.class = ''
  search()
}

function openDialog(row) {
  dialog.id = row?.id || null
  Object.assign(form, row
    ? { sno: row.sno, name: row.name, gender: row.gender, class_name: row.class_name, phone: row.phone }
    : { sno: '', name: '', gender: '男', class_name: '大数据2301', phone: '' })
  dialog.visible = true
  formRef.value?.clearValidate()
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  dialog.loading = true
  try {
    if (dialog.id) {
      await updateStudent(dialog.id, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createStudent({ ...form })
      ElMessage.success('新增成功')
    }
    dialog.visible = false
    load()
  } finally {
    dialog.loading = false
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除学生「${row.name}」？其成绩记录会一并删除。`, '删除确认', {
    type: 'warning'
  })
  await removeStudent(row.id)
  ElMessage.success('已删除')
  if (list.value.length === 1 && query.page > 1) query.page--
  load()
}

onMounted(load)
</script>
