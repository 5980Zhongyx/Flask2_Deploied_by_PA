#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
请求电影详情页并检查返回 HTML 中是否包含 /static/posters/ 的 img 标签，打印匹配行。
用法: python scripts/check_rendered_img.py 44
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def main():
    film_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    app = create_app('development')
    with app.test_client() as client:
        resp = client.get(f'/films/{film_id}')
        print('STATUS:', resp.status_code)
        data = resp.get_data(as_text=True)
        lines = data.splitlines()
        found = [l for l in lines if '/static/posters/' in l]
        if not found:
            print('No /static/posters/ occurrences in response.')
        else:
            print('Found lines:')
            for l in found:
                print(l.strip())

if __name__ == '__main__':
    main()


