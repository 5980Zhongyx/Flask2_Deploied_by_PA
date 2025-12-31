#!/usr/bin/env python3
"""
在生产环境中添加缺失的数据库列
需要在 PythonAnywhere 的 Bash 控制台中运行：
python3 scripts/fix_prod_db.py
"""
import os, sys, sqlite3

# 生产环境的数据库路径
DB = '/home/5980Zhongyx/film_recommendation/instance/app.db'

def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table});")
    cols = [row[1] for row in cur.fetchall()]
    return column in cols

def main():
    if not os.path.exists(DB):
        print("生产数据库未找到:", DB)
        return
    conn = sqlite3.connect(DB)
    try:
        print("检查并添加缺失的列...")
        if not column_exists(conn, 'film', 'like_count'):
            conn.execute("ALTER TABLE film ADD COLUMN like_count INTEGER DEFAULT 0;")
            print("✓ 已添加 like_count 列")
        else:
            print("✓ like_count 列已存在")

        if not column_exists(conn, 'film', 'rating_count'):
            conn.execute("ALTER TABLE film ADD COLUMN rating_count INTEGER DEFAULT 0;")
            print("✓ 已添加 rating_count 列")
        else:
            print("✓ rating_count 列已存在")

        if not column_exists(conn, 'film', 'rating_sum'):
            conn.execute("ALTER TABLE film ADD COLUMN rating_sum INTEGER DEFAULT 0;")
            print("✓ 已添加 rating_sum 列")
        else:
            print("✓ rating_sum 列已存在")

        conn.commit()
        print("数据库迁移完成！")

        # 显示当前 film 表结构
        print("\n当前 film 表结构:")
        cur = conn.execute("PRAGMA table_info(film);")
        for row in cur.fetchall():
            print(f"  {row[1]} ({row[2]})")

    except Exception as e:
        print(f"错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
