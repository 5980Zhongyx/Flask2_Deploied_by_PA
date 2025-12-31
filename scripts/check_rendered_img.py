#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Request film details and print lines containing '/static/posters/' in the HTML.
Usage: python scripts/check_rendered_img.py <film_id>
"""
import sys
import os

# Ensure project root is importable for test client creation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


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
