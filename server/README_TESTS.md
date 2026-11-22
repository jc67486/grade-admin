# 测试与覆盖率

两个后端均用 pytest + pytest-cov，测试独立数据库副本，不污染开发数据。

## 大屏接口（big-screen/server）

```bash
cd server
python -m pytest tests -q --cov=app --cov-report=term-missing
```

```
13 passed，app.py 覆盖率 97%（未覆盖部分为 `if __name__ == "__main__"`）
```

覆盖点：6 个接口的返回结构、`range/top` 参数边界、60s 缓存命中、区域占比合计 100%、城市坐标落在广东经纬度范围、三次产业合计≈全省 GDP、404。

## 成绩管理系统（grade-admin/server）

```bash
cd server
python -m pytest tests -q --cov=app --cov-report=term-missing
```

```
29 passed，app.py 覆盖率 94%
```

覆盖点：登录成功/失败/缺字段、无 token 401、伪造 token 401、教师 vs 学生 403 越权、分页与页码越界、关键字与班级筛选、学号唯一约束、成绩重复拦截、0–100 越界、非数字分数、删除学生级联清理成绩、统计口径（课程均分/及格率/分数段）。

测试中发现并修掉的两个真问题：
1. `datetime.utcnow()` 已废弃 → 改 `datetime.now(timezone.utc)`
2. JWT 密钥 23 字节低于 HS256 建议的 32 字节 → 加长到 48 字节

## 窗口函数分析（grade-admin/server）

```bash
python run_analytics.py
```

`sql/analytics.sql` 里 6 条查询，覆盖常见的分析场景：排名、环比、分位：

| 编号 | 用什么 | 解决什么 |
|---|---|---|
| ① | `RANK() OVER` | 班级平均分排名 |
| ② | `AVG(...) OVER (PARTITION BY)` | 学生总分与班级均分的差额（窗口聚合不折叠明细行） |
| ③ | `LAG() OVER` | 同一学生各科成绩的环比差值，看偏科 |
| ④ | `NTILE(4) OVER` | 每门课按成绩分四档，定位挂科风险 |
| ⑤ | `ROW_NUMBER()` + 外层过滤 | 每门课第一名（窗口函数不能直接写在 WHERE） |
| ⑥ | `SUM(...) OVER ()` | 分数段人数占比 |
