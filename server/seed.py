# -*- coding: utf-8 -*-
"""
学生成绩管理系统 —— 后端（Flask + SQLite + JWT）
运行：python seed.py && python app.py   ->  http://127.0.0.1:5002
账号：teacher/123456（教师）  student/123456（学生）
"""
import os
import sqlite3
import random
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "grades.db")

CLASSES = ["大数据2301", "大数据2302", "软件2301", "软件2302"]
COURSES = [
    ("C001", "数据库原理与应用", 4.0, "陈老师"),
    ("C002", "Python 程序设计", 3.5, "李老师"),
    ("C003", "Web 前端技术", 3.0, "王老师"),
    ("C004", "数据可视化技术", 2.5, "赵老师"),
    ("C005", "Hadoop 应用开发", 3.5, "孙老师"),
    ("C006", "多元统计分析", 3.0, "周老师"),
]
SURNAME = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
GIVEN = ["子涵", "雨欣", "浩然", "思远", "嘉怡", "宇航", "梓萱", "俊杰", "欣怡", "博文",
         "诗涵", "腾飞", "雅琪", "泽宇", "佳琪", "天佑", "梦瑶", "宇轩", "若曦", "子豪"]


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def build():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE user(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        real_name TEXT NOT NULL
    );
    CREATE TABLE student(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sno TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        gender TEXT,
        class_name TEXT,
        phone TEXT
    );
    CREATE TABLE course(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cno TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        credit REAL,
        teacher TEXT
    );
    CREATE TABLE grade(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        score REAL NOT NULL,
        term TEXT NOT NULL
    );
    """)
    cur.executemany("INSERT INTO user(username,password,role,real_name) VALUES(?,?,?,?)", [
        ("teacher", md5("123456"), "teacher", "王建国"),
        ("student", md5("123456"), "student", "张嘉诚"),
    ])
    cur.executemany("INSERT INTO course(cno,name,credit,teacher) VALUES(?,?,?,?)", COURSES)

    rng = random.Random(7)
    students = []
    for i in range(1, 49):
        name = rng.choice(SURNAME) + rng.choice(GIVEN)
        cls = CLASSES[i % len(CLASSES)]
        students.append((f"2023{i:04d}", name, rng.choice(["男", "女"]), cls,
                         f"139{rng.randint(10000000, 99999999)}"))
    cur.executemany(
        "INSERT INTO student(sno,name,gender,class_name,phone) VALUES(?,?,?,?,?)", students)

    rows = []
    for sid in range(1, 49):
        for cid in range(1, 7):
            base = rng.gauss(76, 12)
            score = max(32, min(100, round(base, 1)))
            rows.append((sid, cid, score, "2024-2025-1"))
    cur.executemany(
        "INSERT INTO grade(student_id,course_id,score,term) VALUES(?,?,?,?)", rows)

    cur.execute("CREATE INDEX idx_grade_student ON grade(student_id)")
    cur.execute("CREATE INDEX idx_grade_course ON grade(course_id)")
    cur.execute("CREATE INDEX idx_student_sno ON student(sno)")
    conn.commit()

    n_s = cur.execute("SELECT COUNT(*) FROM student").fetchone()[0]
    n_g = cur.execute("SELECT COUNT(*) FROM grade").fetchone()[0]
    conn.close()
    print(f"[入库] student {n_s} 行 / course {len(COURSES)} 行 / grade {n_g} 行 -> {DB}")


if __name__ == "__main__":
    build()
