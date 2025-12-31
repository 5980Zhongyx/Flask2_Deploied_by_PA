#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def main():
    app = create_app('production')
    with app.app_context():
        from models.film import Film
        print('FILM COUNT:', Film.query.count())

if __name__ == '__main__':
    main()


