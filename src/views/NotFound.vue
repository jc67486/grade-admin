<template>
  <div class="nf">
    <h1>404</h1>
    <p>页面不存在，或你没有访问权限</p>
    <el-button type="primary" @click="$router.replace('/students')">返回首页</el-button>
  </div>
</template>

<style scoped>
.nf {
  height: 100vh;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 10px;
  background: #f4f6fa;
  color: #33415c;
}
.nf h1 { font-size: 64px; margin: 0; color: #2f5bff; }
.nf p { color: #8a94a6; margin-bottom: 8px; }
</style>
