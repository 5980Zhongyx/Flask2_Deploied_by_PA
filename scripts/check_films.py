#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

from app import create_app
from models.film import Film

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    app = create_app("development")
    with app.app_context():
        count = Film.query.count()
        print("Film count:", count)
        films = Film.query.limit(12).all()
        for f in films:
            print(f.id, "|", f.title, "|", f.poster_url)


if __name__ == "__main__":
    main()
