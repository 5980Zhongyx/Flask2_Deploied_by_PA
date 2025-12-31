#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 scripts/poster_mapping.csv 读取 id -> suggested_local_filename 映射，
将结果写回数据库 film.poster_url （仅写文件名，不含路径）。
会先备份 instance/app.db 到 instance/app.db.bak.TIMESTAMP
"""
import os, sys, csv, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import create_app, db

CSV = os.path.join('scripts', 'poster_mapping.csv')
DB_PATH = os.path.join('instance', 'app.db')

def backup_db():
    if not os.path.exists(DB_PATH):
        return None
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    bak = DB_PATH + f'.bak.{ts}'
    shutil.copy2(DB_PATH, bak)
    return bak

def main():
    if not os.path.exists(CSV):
        print('Mapping CSV not found:', CSV)
        return

    # choose environment from FLASK_ENV if set
    env = os.environ.get('FLASK_ENV') or 'development'
    app = create_app(env)

    bak = backup_db()
    if bak:
        print('Database backed up to', bak)
    else:
        print('No DB file found to backup (continuing).')

    posters_dir = os.path.join(app.root_path, 'static', 'posters')
    missing_files = []
    updated = 0

    with app.app_context():
        from models.film import Film
        with open(CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    fid = int(row.get('id') or row.get('film_id') or 0)
                except Exception:
                    continue
                suggested = (row.get('suggested_local_filename') or row.get('filename') or row.get('poster') or '').strip()
                if not suggested:
                    continue
                # prefer basename
                suggested_basename = os.path.basename(suggested)
                fullpath = os.path.join(posters_dir, suggested_basename)
                if not os.path.exists(fullpath):
                    missing_files.append((fid, suggested_basename))
                    # still update DB with the suggested name so it can be fixed later
                film = Film.query.get(fid)
                if not film:
                    continue
                film.poster_url = suggested_basename
                updated += 1
        db.session.commit()

    print('Updates committed:', updated)
    if missing_files:
        print('Missing files (not found in static/posters):', len(missing_files))
        for m in missing_files[:50]:
            print(' ', m)

if __name__ == '__main__':
    main()


