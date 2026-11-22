-- ============================================================
-- 成绩分析 SQL 集（SQLite 3.25+ / MySQL 8 均支持窗口函数）
-- 用途：演示指标体系与窗口函数用法，对应课堂/面试常问的排名、环比、分位
-- ============================================================

-- ① 每个班的平均分与排名（RANK + PARTITION BY）
-- 场景：评奖学金前给班级排序
SELECT
    class_name,
    ROUND(AVG(score), 1)                              AS avg_score,
    COUNT(DISTINCT sno)                               AS stu_cnt,
    RANK() OVER (ORDER BY AVG(score) DESC)            AS class_rank
FROM grade g
JOIN student s ON s.id = g.student_id
GROUP BY class_name;


-- ② 每个学生总分与班级均分之差（窗口聚合不折叠行）
-- 场景：一眼看出谁在拖后腿、谁在拉高平均
SELECT
    s.class_name,
    s.sno,
    s.name,
    SUM(g.score)                                        AS total_score,
    ROUND(AVG(SUM(g.score)) OVER (PARTITION BY s.class_name), 1) AS class_avg_total,
    ROUND(SUM(g.score) - AVG(SUM(g.score)) OVER (PARTITION BY s.class_name), 1) AS diff
FROM grade g
JOIN student s ON s.id = g.student_id
GROUP BY s.id
ORDER BY s.class_name, diff DESC;


-- ③ 每人各科成绩与前一门课的差值（LAG 取上一行）
-- 场景：看单科偏科程度
SELECT
    s.name,
    c.name                                             AS course,
    g.score,
    LAG(g.score) OVER (PARTITION BY g.student_id ORDER BY c.cno) AS prev_score,
    ROUND(g.score - LAG(g.score) OVER (PARTITION BY g.student_id ORDER BY c.cno), 1) AS delta
FROM grade g
JOIN student s ON s.id = g.student_id
JOIN course  c ON c.id = g.course_id
WHERE s.sno = '20230001'
ORDER BY c.cno;


-- ④ 每门课按成绩分成 4 档（NTILE）
-- 场景：分档给平时分 / 定位挂科风险人群
SELECT
    course,
    name,
    score,
    NTILE(4) OVER (PARTITION BY course ORDER BY score DESC) AS quartile
FROM (
    SELECT c.name AS course, s.name, g.score, g.course_id
    FROM grade g
    JOIN student s ON s.id = g.student_id
    JOIN course  c ON c.id = g.course_id
)
ORDER BY course, quartile;


-- ⑤ 每门课的第一名（ROW_NUMBER 后过滤，注意不能直接在 WHERE 用窗口函数）
SELECT course, name, score FROM (
    SELECT
        c.name AS course,
        s.name,
        g.score,
        ROW_NUMBER() OVER (PARTITION BY g.course_id ORDER BY g.score DESC) AS rn
    FROM grade g
    JOIN student s ON s.id = g.student_id
    JOIN course  c ON c.id = g.course_id
) t
WHERE rn = 1
ORDER BY course;


-- ⑥ 各分数段人数与占比（CASE WHEN + 窗口求和）
SELECT
    seg,
    cnt,
    ROUND(cnt * 100.0 / SUM(cnt) OVER (), 1) AS pct
FROM (
    SELECT CASE
             WHEN score >= 90 THEN '优秀(90+)'
             WHEN score >= 80 THEN '良好(80-89)'
             WHEN score >= 70 THEN '中等(70-79)'
             WHEN score >= 60 THEN '及格(60-69)'
             ELSE '不及格(<60)'
           END AS seg,
           COUNT(*) AS cnt
    FROM grade
    GROUP BY seg
)
ORDER BY pct DESC;
