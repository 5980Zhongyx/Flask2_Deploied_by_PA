#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单的 UI smoke test：检查主要页面能否加载（返回 200 / 302），以及静态资源存在性。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def run_tests():
    app = create_app('development')
    with app.test_client() as client:
        routes = ['/', '/films', '/films/1', '/register', '/login']
        results = {}
        for r in routes:
            try:
                resp = client.get(r)
                results[r] = resp.status_code
            except Exception as e:
                results[r] = f'ERROR: {e}'

        # 静态文件
        static_checks = {}
        static_files = ['css/style.css', 'css/ripple.css', 'js/theme.js', 'js/interactions.js']
        for sf in static_files:
            path = os.path.join(app.root_path, 'static', *sf.split('/'))
            static_checks[sf] = os.path.exists(path)

    print('Route status:')
    for r, s in results.items():
        print(f'  {r}: {s}')
    print('\\nStatic files present:')
    for sf, ok in static_checks.items():
        print(f'  {sf}: {ok}')

if __name__ == '__main__':
    run_tests()


