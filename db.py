# 후기를 reviews.db(파일 하나)에 저장하는 도구. 사용자 값은 항상 ? 자리에 넣는다
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "reviews.db"


def connect():
    con = sqlite3.connect(DB_PATH)
    # 표 설계: 번호 · 클래스 번호 · 닉네임 · 별점 · 내용 · 저장 시각 (모두 꼭 있어야 함)
    con.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY,
        class_id INTEGER NOT NULL,
        nickname TEXT NOT NULL,
        rating INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    return con


def add_review(class_id, nickname, rating, content):
    with connect() as con:
        con.execute(
            "INSERT INTO reviews (class_id, nickname, rating, content) VALUES (?, ?, ?, ?)",
            (class_id, nickname, rating, content),
        )


def reviews_of(class_id):
    # 최신순. 저장은 UTC, 꺼낼 때 한국 시간(+9시간)으로 바꿔 준다
    with connect() as con:
        return con.execute(
            "SELECT nickname, rating, content, datetime(created_at, '+9 hours') FROM reviews "
            "WHERE class_id = ? ORDER BY id DESC", (class_id,)
        ).fetchall()
