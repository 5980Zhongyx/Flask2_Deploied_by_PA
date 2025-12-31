#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def main():
    app = create_app('production')
    with app.app_context():
        from models.film import Film
        count = Film.query.count()
        print('Film count:', count)
        films = Film.query.limit(12).all()
        for f in films:
            print(f.id, '|', f.title, '|', f.poster_url)

if __name__ == '__main__':
    main()


