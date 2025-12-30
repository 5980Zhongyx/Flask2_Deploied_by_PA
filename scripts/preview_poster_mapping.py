#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描 static/images/posters/ 中的文件，与数据库中 Film.title 做近似匹配，
生成预览 CSV scripts/poster_match_preview.csv 并在终端打印前20条供人工确认。
"""
import os, sys, csv, re
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def normalize(text):
    if not text:
        return ''
    text = text.lower()
    # remove non-alphanumeric
    text = re.sub(r'[^a-z0-9]+', '', text)
    return text

def best_match(name, candidates):
    best = None
    best_score = 0.0
    for c in candidates:
        score = SequenceMatcher(None, name, c).ratio()
        if score > best_score:
            best_score = score
            best = c
    return best, best_score

def main():
    app = create_app('development')
    with app.app_context():
        from models.film import Film
        posters_dir = os.path.join(app.root_path, 'static', 'images', 'posters')
        files = []
        if os.path.isdir(posters_dir):
            for fn in os.listdir(posters_dir):
                if fn.lower().endswith(('.jpg', '.jpeg', '.png', '.svg', '.webp')):
                    files.append(fn)
        files_norm = {fn: normalize(os.path.splitext(fn)[0]) for fn in files}

        films = Film.query.order_by(Film.id).all()
        rows = []
        filenames = list(files_norm.keys())
        norms = list(files_norm.values())
        for film in films:
            nid = film.id
            title = film.title or ''
            ntitle = normalize(title)
            # Try direct substring match first
            candidate = None
            score = 0.0
            # if any filename contains normalized title
            for fn, nn in files_norm.items():
                if ntitle and ntitle in nn:
                    candidate = fn
                    score = 1.0
                    break
            if not candidate:
                # best similarity on normalized strings
                best_fn, best_score = best_match(ntitle, norms)
                if best_fn:
                    # find original filename with that norm
                    idx = norms.index(best_fn)
                    candidate = filenames[idx]
                    score = best_score
            rows.append((nid, title, candidate or '', score))

        out = os.path.join('scripts', 'poster_match_preview.csv')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'title', 'suggested_filename', 'score'])
            for r in rows:
                writer.writerow(r)

        # print first 20
        print('Preview generated at', out)
        print('First 20 candidates:')
        for r in rows[:20]:
            print(f'id={r[0]} title="{r[1]}" -> file="{r[2]}" score={r[3]:.3f}')

if __name__ == '__main__':
    main()


