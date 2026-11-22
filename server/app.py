# -*- coding: utf-8 -*-
"""
学生成绩管理系统 —— 后端接口（Flask + SQLite + JWT）
统一响应 {code, data, msg}；除 /api/login 外均需 Bearer token
运行：python app.py  ->  http://127.0.0.1:5002
"""
import os
import time
import hashlib
import sqlite3
import datetime as dt

import jwt
from flask import Flask, jsonify, request, g
from flask_cors import CORS

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "grades.db")
SECRET = "grade-admin-demo-secret-key-please-change-in-production"   # 48 bytes，HS256 建议 >=32
TOKEN_TTL = 60 * 60 * 2      # 2 小时

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def ok(data=None, msg="ok"):
    return jsonify({"code": 0, "data": data, "msg": msg})


def fail(msg="参数错误", code=400, http=400):
    return jsonify({"code": code, "data": None, "msg": msg}), http


def make_token(user):
    payload = {
        "uid": user["id"], "username": user["username"], "role": user["role"],
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=TOKEN_TTL)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def auth_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*a, **kw):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return fail("未登录或 token 缺失", 401, 401)
        try:
            g.user = jwt.decode(header[7:], SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return fail("登录已过期，请重新登录", 401, 401)
        except Exception:
            return fail("token 无效", 401, 401)
        return fn(*a, **kw)
    return wrapper


@app.post("/api/login")
def login():
    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    if not username or not password:
        return fail("用户名和密码不能为空")
    with conn() as c:
        row = c.execute("SELECT * FROM user WHERE username=?", (username,)).fetchone()
    if not row or row["password"] != md5(password):
        return fail("用户名或密码错误", 400)
    return ok({
        "token": make_token(row),
        "user": {"id": row["id"], "username": row["username"],
                 "role": row["role"], "name": row["real_name"]}
    })


@app.get("/api/me")
@auth_required
def me():
    with conn() as c:
        row = c.execute("SELECT id,username,role,real_name FROM user WHERE id=?",
                        (g.user["uid"],)).fetchone()
    return ok(dict(row) if row else None)


@app.get("/api/students")
@auth_required
def list_students():
    page = request.args.get("page", "1")
    size = request.args.get("size", "10")
    keyword = (request.args.get("keyword") or "").strip()
    cls = (request.args.get("class") or "").strip()
    if not page.isdigit() or not size.isdigit():
        return fail("分页参数必须为正整数")
    page, size = max(1, int(page)), min(100, max(1, int(size)))

    where, args = [], []
    if keyword:
        where.append("(name LIKE ? OR sno LIKE ?)")
        args += [f"%{keyword}%", f"%{keyword}%"]
    if cls:
        where.append("class_name = ?")
        args.append(cls)
    clause = ("WHERE " + " AND ".join(where)) if where else ""

    with conn() as c:
        total = c.execute(f"SELECT COUNT(*) FROM student {clause}", args).fetchone()[0]
        rows = c.execute(
            f"SELECT * FROM student {clause} ORDER BY sno LIMIT ? OFFSET ?",
            args + [size, (page - 1) * size]).fetchall()
    return ok({"list": [dict(r) for r in rows], "total": total, "page": page, "size": size})


@app.post("/api/students")
@auth_required
def create_student():
    if g.user["role"] != "teacher":
        return fail("无权限：仅教师可维护学生", 403, 403)
    b = request.get_json(silent=True) or {}
    sno, name = (b.get("sno") or "").strip(), (b.get("name") or "").strip()
    if not sno or not name:
        return fail("学号与姓名必填")
    if len(sno) != 8 or not sno.isdigit():
        return fail("学号必须为 8 位数字")
    try:
        with conn() as c:
            cur = c.execute(
                "INSERT INTO student(sno,name,gender,class_name,phone) VALUES(?,?,?,?,?)",
                (sno, name, b.get("gender") or "男", b.get("class_name") or "", b.get("phone") or ""))
            c.commit()
            return ok({"id": cur.lastrowid})
    except sqlite3.IntegrityError:
        return fail("学号已存在")


@app.put("/api/students/<int:sid>")
@auth_required
def update_student(sid):
    if g.user["role"] != "teacher":
        return fail("无权限：仅教师可维护学生", 403, 403)
    b = request.get_json(silent=True) or {}
    with conn() as c:
        c.execute("UPDATE student SET name=?,gender=?,class_name=?,phone=? WHERE id=?",
                  (b.get("name"), b.get("gender"), b.get("class_name"), b.get("phone"), sid))
        c.commit()
    return ok()


@app.delete("/api/students/<int:sid>")
@auth_required
def delete_student(sid):
    if g.user["role"] != "teacher":
        return fail("无权限：仅教师可维护学生", 403, 403)
    with conn() as c:
        c.execute("DELETE FROM student WHERE id=?", (sid,))
        c.execute("DELETE FROM grade WHERE student_id=?", (sid,))
        c.commit()
    return ok()


@app.get("/api/courses")
@auth_required
def list_courses():
    with conn() as c:
        rows = c.execute("SELECT * FROM course ORDER BY cno").fetchall()
    return ok({"list": [dict(r) for r in rows]})


@app.get("/api/grades")
@auth_required
def list_grades():
    keyword = (request.args.get("keyword") or "").strip()
    course_id = request.args.get("course_id", "")
    sql = """SELECT g.id, s.sno, s.name, s.class_name, c.name AS course, c.credit,
                    g.score, g.term
             FROM grade g JOIN student s ON s.id=g.student_id
             JOIN course c ON c.id=g.course_id WHERE 1=1"""
    args = []
    if keyword:
        sql += " AND (s.name LIKE ? OR s.sno LIKE ?)"
        args += [f"%{keyword}%", f"%{keyword}%"]
    if course_id.isdigit():
        sql += " AND g.course_id=?"
        args.append(int(course_id))
    sql += " ORDER BY s.sno, c.cno"
    with conn() as c:
        rows = c.execute(sql, args).fetchall()
    return ok({"list": [dict(r) for r in rows]})


@app.post("/api/grades")
@auth_required
def create_grade():
    if g.user["role"] != "teacher":
        return fail("无权限：仅教师可录入成绩", 403, 403)
    b = request.get_json(silent=True) or {}
    sid, cid, score = b.get("student_id"), b.get("course_id"), b.get("score")
    if not sid or not cid:
        return fail("学生与课程必选")
    try:
        score = float(score)
    except (TypeError, ValueError):
        return fail("成绩必须为数字")
    if not (0 <= score <= 100):
        return fail("成绩需在 0–100 之间")
    with conn() as c:
        dup = c.execute("SELECT 1 FROM grade WHERE student_id=? AND course_id=?",
                        (sid, cid)).fetchone()
        if dup:
            return fail("该学生该课程已有成绩")
        c.execute("INSERT INTO grade(student_id,course_id,score,term) VALUES(?,?,?,?)",
                  (sid, cid, score, b.get("term") or "2024-2025-1"))
        c.commit()
    return ok()


@app.get("/api/stats")
@auth_required
def stats():
    with conn() as c:
        by_course = c.execute("""
            SELECT c.name AS course, ROUND(AVG(g.score),1) AS avg_score,
                   MAX(g.score) AS max_score, MIN(g.score) AS min_score,
                   SUM(CASE WHEN g.score>=60 THEN 1 ELSE 0 END)*100.0/COUNT(*) AS pass_rate
            FROM grade g JOIN course c ON c.id=g.course_id GROUP BY g.course_id ORDER BY c.cno
        """).fetchall()
        dist = c.execute("""
            SELECT CASE
                WHEN score>=90 THEN '优秀(90+)'
                WHEN score>=80 THEN '良好(80-89)'
                WHEN score>=70 THEN '中等(70-79)'
                WHEN score>=60 THEN '及格(60-69)'
                ELSE '不及格(<60)' END AS seg, COUNT(*) AS cnt
            FROM grade GROUP BY seg
        """).fetchall()
        by_class = c.execute("""
            SELECT s.class_name, ROUND(AVG(g.score),1) AS avg_score, COUNT(DISTINCT s.id) AS stu_cnt
            FROM grade g JOIN student s ON s.id=g.student_id GROUP BY s.class_name
        """).fetchall()
    return ok({
        "by_course": [dict(r) for r in by_course],
        "distribution": [dict(r) for r in dist],
        "by_class": [dict(r) for r in by_class],
    })


@app.get("/api/health")
def health():
    return ok({"status": "up", "ts": int(time.time())})


@app.errorhandler(404)
def nf(_):
    return jsonify({"code": 404, "data": None, "msg": "接口不存在"}), 404


if __name__ == "__main__":
    if not os.path.exists(DB):
        raise SystemExit("请先运行 python seed.py")
    app.run(host="127.0.0.1", port=5002, debug=False)
