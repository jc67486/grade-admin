# 学生成绩管理系统

前后端分离的教务管理系统：Vue 3 + Element Plus 前端（6 个页面 + 角色权限路由 + 通用表格组件），Flask + JWT 后端（48 名学生 / 6 门课程 / 288 条成绩）。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3、Vite 5、vue-router 4、Pinia 2、Element Plus、Axios |
| 后端 | Flask 3、PyJWT、SQLite、MD5 加盐（演示用，生产应换 bcrypt） |

## 页面

| 路由 | 页面 | 权限 |
|---|---|---|
| /login | 登录 | 公开 |
| /students | 学生管理（表格 / 搜索 / 分页 / 增删改） | 教师 |
| /courses | 课程管理 | 登录 |
| /grades | 成绩录入 + 成绩明细 | 登录（录入仅教师） |
| /stats | 成绩统计（各课平均分 / 及格率 / 分数段） | 登录 |
| /profile | 个人中心 | 登录 |

## 快速开始

```bash
# 1. 后端
cd server
pip install flask flask-cors pyjwt
python seed.py      # 生成 grades.db（48 学生 / 6 课程 / 288 成绩）
python app.py       # http://127.0.0.1:5002

# 2. 前端
cd ..
npm install
npm run dev         # http://127.0.0.1:5174
```

演示账号：`teacher / 123456`（教师）、`student / 123456`（学生）

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/login | 登录签发 JWT（2 小时） |
| GET | /api/me | 当前用户 |
| GET | /api/students?page&size&keyword&class | 分页查询（含搜索） |
| POST/PUT/DELETE | /api/students[/:id] | 增删改（仅教师，越权返回 403） |
| GET | /api/courses | 课程列表 |
| GET | /api/grades?keyword&course_id | 成绩明细 |
| POST | /api/grades | 成绩录入（重复 / 越界校验） |
| GET | /api/stats | 各课均分 + 分数段分布 + 班级均分 |

## 前端做了什么

- **路由守卫**：token 校验、`meta.roles` 动态过滤菜单、未登录携带 `redirect` 回跳、404 兜底
- **状态持久化**：Pinia + localStorage，刷新不丢登录态，登出清空并重置路由
- **请求层**：双拦截器统一注入 Bearer token、错误码映射；401 加重定向锁，避免并发请求重复弹窗
- **通用表格**：列配置 + 分页 + 搜索 + loading + 空状态 + 操作列插槽，三处页面复用同一套配置
- **表单校验**：必填 / 0–100 范围 / 8 位学号 / 手机号正则，行内提示 + 提交 loading 锁
- **交互**：删除与退出二次确认、失败 toast 不清空已有数据、成绩按分数段着色

## 测试

`ash
cd server
python -m pytest tests -q --cov=app --cov-report=term-missing   # 29 passed, 94%
python run_analytics.py                                          # 6 条窗口函数分析
`

## 实测数据

- 构建产物：1.6 MB（Element Plus 全量引入）；6 个页面各自独立 chunk，最大 5.7 KB
- 接口：登录 → 分页查询 → 成绩明细 → 统计全链路联调通过；无 token 访问返回 401
- 数据量：48 名学生 / 6 门课程 / 288 条成绩

## 可改进点

1. Element Plus 全量引入导致 1.2 MB 主包，应改 `unplugin-vue-components` 按需引入
2. 密码用 MD5 仅为演示，生产环境应换 bcrypt + 加盐 + 登录限流
3. 成绩查询未做服务端分页，数据量大时需补 page/size 与索引
