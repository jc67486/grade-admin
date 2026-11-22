# -*- coding: utf-8 -*-
import os
import sys
import shutil

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.dirname(HERE)
sys.path.insert(0, SERVER_DIR)

import app as app_module  # noqa: E402

SRC_DB = os.path.join(SERVER_DIR, "grades.db")


@pytest.fixture()
def client(tmp_path):
    """每个测试用独立数据库副本，避免污染开发数据"""
    tmp_db = tmp_path / "grades.db"
    shutil.copy(SRC_DB, tmp_db)
    app_module.DB = str(tmp_db)
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as c:
        yield c


def login(client, username="teacher", password="123456"):
    r = client.post("/api/login", json={"username": username, "password": password})
    return r.get_json()


@pytest.fixture()
def teacher_headers(client):
    data = login(client)
    return {"Authorization": f"Bearer {data['data']['token']}"}


@pytest.fixture()
def student_headers(client):
    data = login(client, "student")
    return {"Authorization": f"Bearer {data['data']['token']}"}
