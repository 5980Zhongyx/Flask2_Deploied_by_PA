#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出数据库中 film.poster_url 指向本地 posters/ 但文件不存在的记录，
以及 poster_url 为空的记录，便于后续补全。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def main():
    app = create_app('production')
    posters_dir = os.path.join(app.root_path, 'static', 'posters')
    with app.app_context():
        from models.film import Film
        films = Film.query.order_by(Film.id).all()
        missing_file = []
        empty_poster = []
        remote_poster = []
        for f in films:
            pu = f.poster_url or ''
            if not pu:
                empty_poster.append((f.id, f.title))
            elif pu.startswith('http') or pu.startswith('//'):
                remote_poster.append((f.id, f.title, pu))
            else:
                path = os.path.join(posters_dir, pu)
                if not os.path.exists(path):
                    missing_file.append((f.id, f.title, pu))

        print('TOTAL_FILMS:', len(films))
        print('EMPTY_POSTER_COUNT:', len(empty_poster))
        print('MISSING_FILE_COUNT:', len(missing_file))
        print('REMOTE_POSTER_COUNT:', len(remote_poster))
        if empty_poster:
            print('\\n-- Empty poster entries (id,title) --')
            for r in empty_poster[:50]:
                print(r)
        if missing_file:
            print('\\n-- Missing file entries (id,title,poster_url) --')
            for r in missing_file[:100]:
                print(r)
        if remote_poster:
            print('\\n-- Remote poster examples (id,title,url) --')
            for r in remote_poster[:10]:
                print(r)

if __name__ == '__main__':
    main()


