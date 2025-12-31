#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from models.film import Film

app = create_app('development')
with app.app_context():
    f = Film.query.get(33)
    if not f:
        print("Film 33 not found")
    else:
        print("Title:", f.title)
        print("Poster URL:", f.poster_url)
        exists = app.jinja_env.globals['static_file_exists']('posters/' + (f.poster_url or ''))
        print("static_file_exists:", exists)
        print("Static poster path:", os.path.join(app.static_folder, 'posters', f.poster_url or ''))

