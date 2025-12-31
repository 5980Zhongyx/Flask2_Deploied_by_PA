#!/usr/bin/env python3
import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'app.db')
STATIC_POSTERS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'posters')

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(film)")
    cols = cur.fetchall()
    print("film table columns:")
    for c in cols:
        print(c)

    cur.execute("SELECT id, title, poster_url FROM film")
    rows = cur.fetchall()
    missing = []
    for id, title, poster in rows:
        if not poster:
            continue
        poster_path = os.path.join(STATIC_POSTERS, poster)
        if poster.startswith('http') or poster.startswith('//'):
            # remote poster, skip file existence check
            continue
        if not os.path.exists(poster_path):
            missing.append((id, title, poster))

    print("\\nMissing local poster files:")
    for m in missing:
        print(m)
    print("\\nTotal films:", len(rows))
    print("Total missing posters:", len(missing))

    conn.close()

if __name__ == '__main__':
    main()


