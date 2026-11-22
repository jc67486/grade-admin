# -*- coding: utf-8 -*-
"""
把 sql/analytics.sql 里的分析查询逐条跑一遍并打印结果。
运行：python run_analytics.py
"""
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "grades.db")
SQL_FILE = os.path.join(HERE, "sql", "analytics.sql")


def split_statements(sql_text):
    """按分号切分，保留前面最近的一条注释作为标题"""
    blocks, buf, title = [], [], ""
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            if not buf:
                title = stripped.lstrip("- ").strip()
            continue
        buf.append(line)
        if stripped.endswith(";"):
            blocks.append((title, "\n".join(buf)))
            buf, title = [], ""
    return blocks


def main():
    if not os.path.exists(DB):
        raise SystemExit("请先运行 python seed.py 生成 grades.db")

    with open(SQL_FILE, encoding="utf-8") as f:
        blocks = split_statements(f.read())

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    for idx, (title, stmt) in enumerate(blocks, 1):
        if not stmt.strip():
            continue
        rows = cur.execute(stmt).fetchall()
        print(f"\n{'=' * 70}")
        print(f"[{idx}] {title}")
        print("-" * 70)
        if not rows:
            print("（无结果）")
            continue
        cols = rows[0].keys()
        print(" | ".join(f"{c:<12}" for c in cols))
        for r in rows[:8]:
            print(" | ".join(f"{str(r[c]):<12}" for c in cols))
        if len(rows) > 8:
            print(f"... 共 {len(rows)} 行")
    conn.close()


if __name__ == "__main__":
    main()
