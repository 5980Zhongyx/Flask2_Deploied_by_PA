#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
read id -> suggested_local_filename mapping from scripts/poster_mapping.csv,
write result back to database film.poster_url (only write filename, no path).
backup instance/app.db to instance/app.db.bak.TIMESTAMP first
"""
import csv
import datetime
import os
import shutil
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import create_app, db  # noqa: E402

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

    # choose environment from FLASK_ENV if set in environment
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
                suggested = (row.get('suggested_local_filename') or
                             row.get('filename') or row.get('poster') or '').strip()
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
        print('Missing files (not found in static/posters):',
              len(missing_files))
        for m in missing_files[:50]:
            print(' ', m)


if __name__ == '__main__':
    main()
