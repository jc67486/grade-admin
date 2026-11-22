<template>
  <div>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-card__label">平均分（全部课程）</div>
        <div class="stat-card__value">{{ overall.avg }}</div>
        <div class="stat-card__foot">共 {{ overall.count }} 条成绩记录</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">最高分</div>
        <div class="stat-card__value">{{ overall.max }}</div>
        <div class="stat-card__foot">{{ overall.maxCourse }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">最低分</div>
        <div class="stat-card__value">{{ overall.min }}</div>
        <div class="stat-card__foot">{{ overall.minCourse }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">总体及格率</div>
        <div class="stat-card__value">{{ overall.passRate }}%</div>
        <div class="stat-card__foot">≥60 分占比</div>
      </div>
    </div>

    <div class="page-card" style="margin-bottom: 16px">
      <div class="page-head"><h2>各课程平均分与及格率</h2></div>
      <el-table :data="byCourse" border stripe :header-cell-style="{ background: '#f7f9fc', color: '#33415c', fontWeight: 600 }">
        <el-table-column prop="course" label="课程" width="220" />
        <el-table-column prop="avg_score" label="平均分" width="100" align="center" />
        <el-table-column prop="max_score" label="最高" width="90" align="center" />
        <el-table-column prop="min_score" label="最低" width="90" align="center" />
        <el-table-column label="及格率" min-width="220">
          <template #default="{ row }">
            <div class="bar">
              <div class="bar__inner" :style="{ width: row.pass_rate + '%' }"></div>
            </div>
            <span class="bar__text">{{ row.pass_rate }}%</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="page-card">
      <div class="page-head"><h2>分数段分布</h2></div>
      <div class="dist">
        <div v-for="d in distribution" :key="d.seg" class="dist__item">
          <div class="dist__bar" :style="{ height: barHeight(d.cnt) }">
            <span>{{ d.cnt }}</span>
          </div>
          <div class="dist__label">{{ d.seg }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getStats } from '@/api/modules'

const byCourse = ref([])
const distribution = ref([])
const byClass = ref([])
const loading = ref(false)

const overall = computed(() => {
  if (!byCourse.value.length) return { avg: '-', max: '-', min: '-', passRate: '-', count: 0, maxCourse: '', minCourse: '' }
  const total = byCourse.value.reduce((a, c) => a + c.avg_score, 0)
  const maxRow = byCourse.value.reduce((a, c) => (c.max_score > a.max_score ? c : a))
  const minRow = byCourse.value.reduce((a, c) => (c.min_score < a.min_score ? c : a))
  const pass = byCourse.value.reduce((a, c) => a + Number(c.pass_rate), 0)
  return {
    avg: (total / byCourse.value.length).toFixed(1),
    max: maxRow.max_score,
    min: minRow.min_score,
    passRate: (pass / byCourse.value.length).toFixed(1),
    count: distribution.value.reduce((a, c) => a + c.cnt, 0),
    maxCourse: maxRow.course,
    minCourse: minRow.course
  }
})

function barHeight(cnt) {
  const max = Math.max(...distribution.value.map((d) => d.cnt), 1)
  return Math.max(6, (cnt / max) * 160) + 'px'
}

onMounted(async () => {
  const data = await getStats()
  byCourse.value = data.by_course
  distribution.value = data.distribution
  byClass.value = data.by_class
})
</script>

<style scoped>
.bar {
  display: inline-block;
  width: 65%;
  height: 10px;
  background: #eef1f6;
  border-radius: 6px;
  overflow: hidden;
  vertical-align: middle;
}
.bar__inner {
  height: 100%;
  background: linear-gradient(90deg, #2f5bff, #6d94ff);
  border-radius: 6px;
}
.bar__text { margin-left: 8px; color: #4a5568; font-size: 13px; }
.dist {
  display: flex;
  align-items: flex-end;
  gap: 34px;
  height: 210px;
  padding: 10px 8px 0;
}
.dist__item { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; flex: 1; }
.dist__bar {
  width: 64px;
  background: linear-gradient(180deg, #6d94ff, #2f5bff);
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  padding-top: 4px;
}
.dist__label { margin-top: 8px; color: #5c6b82; font-size: 12px; }
</style>
