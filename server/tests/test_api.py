# -*- coding: utf-8 -*-
"""成绩管理系统接口测试：鉴权、角色越权、参数校验、数据一致性、统计口径"""


# ---------------- 鉴权 ----------------
def test_login_ok(client):
    body = client.post("/api/login", json={"username": "teacher", "password": "123456"}).get_json()
    assert body["code"] == 0
    assert body["data"]["token"]
    assert body["data"]["user"]["role"] == "teacher"


def test_login_wrong_password(client):
    r = client.post("/api/login", json={"username": "teacher", "password": "bad"})
    assert r.status_code == 400
    assert r.get_json()["code"] == 400


def test_login_missing_field(client):
    assert client.post("/api/login", json={"username": "teacher"}).status_code == 400


def test_no_token_401(client):
    r = client.get("/api/students")
    assert r.status_code == 401
    assert r.get_json()["code"] == 401


def test_bad_token_401(client):
    r = client.get("/api/students", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401


def test_me(client, teacher_headers):
    body = client.get("/api/me", headers=teacher_headers).get_json()
    assert body["data"]["username"] == "teacher"


# ---------------- 学生查询 ----------------
def test_students_pagination(client, teacher_headers):
    body = client.get("/api/students?page=1&size=5", headers=teacher_headers).get_json()
    assert body["data"]["total"] == 48
    assert len(body["data"]["list"]) == 5


def test_students_page2(client, teacher_headers):
    p1 = client.get("/api/students?page=1&size=5", headers=teacher_headers).get_json()["data"]
    p2 = client.get("/api/students?page=2&size=5", headers=teacher_headers).get_json()["data"]
    assert {s["id"] for s in p1["list"]}.isdisjoint({s["id"] for s in p2["list"]})


def test_students_invalid_page(client, teacher_headers):
    assert client.get("/api/students?page=abc", headers=teacher_headers).status_code == 400


def test_students_keyword(client, teacher_headers):
    body = client.get("/api/students?keyword=2023000", headers=teacher_headers).get_json()
    assert body["data"]["total"] >= 1
    assert all("2023000" in s["sno"] or "2023000" in s["name"] for s in body["data"]["list"])


def test_students_filter_class(client, teacher_headers):
    body = client.get("/api/students?class=软件2301", headers=teacher_headers).get_json()
    assert all(s["class_name"] == "软件2301" for s in body["data"]["list"])


# ---------------- 学生增删改 + 权限 ----------------
def test_create_student_ok(client, teacher_headers):
    r = client.post("/api/students", headers=teacher_headers,
                    json={"sno": "20239999", "name": "测试同学", "gender": "男",
                          "class_name": "软件2301", "phone": "13900000000"})
    assert r.get_json()["code"] == 0
    assert r.get_json()["data"]["id"] > 0


def test_create_student_duplicate_no(client, teacher_headers):
    payload = {"sno": "20239999", "name": "测试同学", "class_name": "软件2301"}
    client.post("/api/students", headers=teacher_headers, json=payload)
    r = client.post("/api/students", headers=teacher_headers, json=payload)
    assert r.status_code == 400


def test_create_student_bad_sno(client, teacher_headers):
    r = client.post("/api/students", headers=teacher_headers,
                    json={"sno": "123", "name": "短学号"})
    assert r.status_code == 400


def test_create_student_forbidden_for_student(client, student_headers):
    r = client.post("/api/students", headers=student_headers,
                    json={"sno": "20238888", "name": "越权"})
    assert r.status_code == 403


def test_update_student(client, teacher_headers):
    sid = client.post("/api/students", headers=teacher_headers,
                      json={"sno": "20239777", "name": "改名前", "class_name": "软件2301"}
                      ).get_json()["data"]["id"]
    r = client.put(f"/api/students/{sid}", headers=teacher_headers,
                   json={"name": "改名后", "gender": "女", "class_name": "大数据2301"})
    assert r.get_json()["code"] == 0
    body = client.get("/api/students?keyword=20239777", headers=teacher_headers).get_json()
    assert body["data"]["list"][0]["name"] == "改名后"


def test_delete_student_cascade_grade(client, teacher_headers):
    """删除学生后，其成绩记录应一并清理"""
    created = client.post("/api/students", headers=teacher_headers,
                          json={"sno": "20239666", "name": "待删同学", "class_name": "软件2301"}
                          ).get_json()["data"]["id"]
    course_id = client.get("/api/courses", headers=teacher_headers).get_json()["data"]["list"][0]["id"]
    client.post("/api/grades", headers=teacher_headers,
                json={"student_id": created, "course_id": course_id, "score": 88})

    before = len(client.get("/api/grades", headers=teacher_headers).get_json()["data"]["list"])
    client.delete(f"/api/students/{created}", headers=teacher_headers)
    after = len(client.get("/api/grades", headers=teacher_headers).get_json()["data"]["list"])
    assert before - after == 1


def test_delete_forbidden_for_student(client, student_headers):
    assert client.delete("/api/students/1", headers=student_headers).status_code == 403


# ---------------- 课程 / 成绩 ----------------
def test_courses(client, teacher_headers):
    rows = client.get("/api/courses", headers=teacher_headers).get_json()["data"]["list"]
    assert len(rows) == 6
    assert {"cno", "name", "credit", "teacher"} <= set(rows[0].keys())


def test_grades_list(client, teacher_headers):
    rows = client.get("/api/grades", headers=teacher_headers).get_json()["data"]["list"]
    assert len(rows) == 288


def test_grade_create_ok(client, teacher_headers):
    sid = client.post("/api/students", headers=teacher_headers,
                      json={"sno": "20239555", "name": "录成绩", "class_name": "软件2301"}
                      ).get_json()["data"]["id"]
    cid = client.get("/api/courses", headers=teacher_headers).get_json()["data"]["list"][0]["id"]
    r = client.post("/api/grades", headers=teacher_headers,
                    json={"student_id": sid, "course_id": cid, "score": 91.5})
    assert r.get_json()["code"] == 0


def test_grade_duplicate_rejected(client, teacher_headers):
    sid = client.post("/api/students", headers=teacher_headers,
                      json={"sno": "20239444", "name": "重复录", "class_name": "软件2301"}
                      ).get_json()["data"]["id"]
    cid = client.get("/api/courses", headers=teacher_headers).get_json()["data"]["list"][0]["id"]
    client.post("/api/grades", headers=teacher_headers,
                json={"student_id": sid, "course_id": cid, "score": 70})
    r = client.post("/api/grades", headers=teacher_headers,
                    json={"student_id": sid, "course_id": cid, "score": 80})
    assert r.status_code == 400


def test_grade_score_out_of_range(client, teacher_headers):
    sid = client.post("/api/students", headers=teacher_headers,
                      json={"sno": "20239333", "name": "越界", "class_name": "软件2301"}
                      ).get_json()["data"]["id"]
    cid = client.get("/api/courses", headers=teacher_headers).get_json()["data"]["list"][0]["id"]
    for bad in (101, -1):
        r = client.post("/api/grades", headers=teacher_headers,
                        json={"student_id": sid, "course_id": cid, "score": bad})
        assert r.status_code == 400


def test_grade_score_not_number(client, teacher_headers):
    r = client.post("/api/grades", headers=teacher_headers,
                    json={"student_id": 1, "course_id": 1, "score": "优秀"})
    assert r.status_code == 400


def test_grade_missing_student(client, teacher_headers):
    r = client.post("/api/grades", headers=teacher_headers, json={"course_id": 1, "score": 60})
    assert r.status_code == 400


def test_grade_forbidden_for_student(client, student_headers):
    r = client.post("/api/grades", headers=student_headers,
                    json={"student_id": 1, "course_id": 1, "score": 100})
    assert r.status_code == 403


# ---------------- 统计口径 ----------------
def test_stats_shape(client, teacher_headers):
    d = client.get("/api/stats", headers=teacher_headers).get_json()["data"]
    assert len(d["by_course"]) == 6
    assert sum(x["cnt"] for x in d["distribution"]) == 288
    assert len(d["by_class"]) == 4


def test_stats_score_range(client, teacher_headers):
    d = client.get("/api/stats", headers=teacher_headers).get_json()["data"]
    for row in d["by_course"]:
        assert 0 <= row["min_score"] <= row["avg_score"] <= row["max_score"] <= 100
        assert 0 <= row["pass_rate"] <= 100


def test_404(client):
    assert client.get("/api/nope").status_code == 404
