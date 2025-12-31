#!/usr/bin/env python3
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "instance", "app.db")


def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table});")
    cols = [row[1] for row in cur.fetchall()]
    return column in cols


def main():
    if not os.path.exists(DB):
        print("DB not found:", DB)
        return
    conn = sqlite3.connect(DB)
    try:
        if not column_exists(conn, "film", "like_count"):
            conn.execute("ALTER TABLE film ADD COLUMN like_count INTEGER DEFAULT 0;")
            print("Added like_count")
        if not column_exists(conn, "film", "rating_count"):
            conn.execute("ALTER TABLE film ADD COLUMN rating_count INTEGER DEFAULT 0;")
            print("Added rating_count")
        if not column_exists(conn, "film", "rating_sum"):
            conn.execute("ALTER TABLE film ADD COLUMN rating_sum INTEGER DEFAULT 0;")
            print("Added rating_sum")
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
