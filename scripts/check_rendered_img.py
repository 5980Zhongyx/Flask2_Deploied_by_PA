#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Request film details and check and print the lines that contain /static/posters/ in the HTML response.
Usage: python scripts/check_rendered_img.py 44
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
        found = [line for line in lines if '/static/posters/' in line]
        if not found:
            print('No /static/posters/ occurrences in response.')
        else:
            print('Found lines:')
            for line in found:
                print(line.strip())

if __name__ == '__main__':
    main()


