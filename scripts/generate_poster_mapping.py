#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成电影海报本地化映射表（CSV）

该脚本会读取数据库中所有 Film 的 poster_url 字段，并生成一个 CSV：
id,title,current_poster_url,suggested_local_filename

你可以把图片上传到 static/images/posters/，然后根据 suggested_local_filename 更新数据库 poster_url 字段为该文件名。
"""
import csv
import os
import re
import sys
# 添加项目根目录到 Python 路径，确保从 scripts 目录运行时能导入 app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def main(output='scripts/poster_mapping.csv'):
    app = create_app('development')
    with app.app_context():
        from models.film import Film
        films = Film.query.all()

        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'title', 'current_poster_url', 'suggested_local_filename'])
            for film in films:
                current = film.poster_url or ''
                # 建议文件名：id-slug.ext（若 remote 有扩展名则保留）
                ext = os.path.splitext(current)[1] if current and '.' in current else '.jpg'
                slug = slugify(film.title or f'film-{film.id}')
                suggested = f'{film.id}-{slug}{ext}'
                writer.writerow([film.id, film.title, current, suggested])

        print(f'已生成映射：{output} （共 {len(films)} 条）')

if __name__ == '__main__':
    main()


