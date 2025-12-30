#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中 poster_url 的更新情况并打印样本
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def main():
    app = create_app('development')
    with app.app_context():
        from models.film import Film
        total = Film.query.count()
        with_post = Film.query.filter(Film.poster_url.isnot(None)).count()
        sample = Film.query.filter(Film.poster_url.isnot(None)).limit(10).all()
        sample_rows = [(f.id, f.title, f.poster_url) for f in sample]
        print("TOTAL_FILMS:", total)
        print("FILMS_WITH_POSTER:", with_post)
        print("SAMPLE:", sample_rows)

if __name__ == '__main__':
    main()


