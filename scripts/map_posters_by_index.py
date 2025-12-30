#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 static/posters 中按字母顺序的文件依次映射到数据库中 Film.id 的升序。
生成预览 scripts/poster_mapping_by_index.csv 并打印前20条供确认。
（请在确认后运行脚本 apply_posters_to_db.py 来执行数据库更新）
"""
import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def main():
    app = create_app('development')
    with app.app_context():
        from models.film import Film
        posters_dir = os.path.join(app.root_path, 'static', 'posters')
        files = []
        if os.path.isdir(posters_dir):
            files = sorted([f for f in os.listdir(posters_dir) if f.lower().endswith(('.jpg','.jpeg','.png','.svg','.webp'))])

        films = Film.query.order_by(Film.id).all()
        mapping = []
        for i, film in enumerate(films):
            fn = files[i] if i < len(files) else ''
            mapping.append((film.id, film.title, fn))

        out = os.path.join('scripts', 'poster_mapping_by_index.csv')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id','title','filename'])
            for r in mapping:
                writer.writerow(r)

        print('Preview mapping written to', out)
        for r in mapping[:20]:
            print(f'id={r[0]} title="{r[1]}" -> file="{r[2]}"')

if __name__ == '__main__':
    main()


