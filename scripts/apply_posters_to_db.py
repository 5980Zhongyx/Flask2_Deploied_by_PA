#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 scripts/poster_mapping_by_index.csv 中的映射写入数据库 film.poster_url 字段。
会先备份 instance/app.db 到 instance/app.db.bak.TIMESTAMP
运行前请确保已上传图片到 static/posters/
"""
import os, sys, csv, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import create_app, db

CSV = os.path.join('scripts', 'poster_mapping_by_index.csv')
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

    # Respect FLASK_ENV if set so we can target production/dev appropriately
    env = os.environ.get('FLASK_ENV') or 'development'
    app = create_app(env)
    bak = backup_db()
    if bak:
        print('Database backed up to', bak)
    else:
        print('No DB file found to backup (continuing).')

    with app.app_context():
        from models.film import Film
        updates = 0
        missing_files = []
        posters_dir = os.path.join(app.root_path, 'static', 'posters')
        with open(CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fid = int(row['id'])
                fn = row.get('filename') or row.get('suggested_filename') or ''
                if not fn:
                    continue
                full = os.path.join(posters_dir, fn)
                if not os.path.exists(full):
                    missing_files.append(fn)
                    continue
                film = Film.query.get(fid)
                if not film:
                    continue
                film.poster_url = fn
                updates += 1
        db.session.commit()
        print('Updates committed:', updates)
        if missing_files:
            print('Missing files (not updated):', len(missing_files))
            for m in missing_files[:20]:
                print(' ', m)

if __name__ == '__main__':
    main()


