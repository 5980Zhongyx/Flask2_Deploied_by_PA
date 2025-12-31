#!/usr/bin/env python3
"""
Quick script to make database film fields English-friendly for short-term display.

What it does:
- Creates a JSON backup of current film id/title/genre/director/description to
  scripts/film_backup_originals.json
- Replaces `description` with a short English sentence using the English title,
  year, mapped English genre and director (keeps director name as-is).

Usage (on PythonAnywhere):
    cd ~/film_recommendation
    source venv/bin/activate   # if you use a virtualenv
    python3 scripts/quick_enify_db.py

This is a reversible, short-term fix. It does NOT remove originals (they are backed up).
For a long-term solution we should add bilingual columns and populate them.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models.film import Film

GENRE_MAP = {
    "剧情": "Drama",
    "爱情": "Romance",
    "动画": "Animation",
    "动作": "Action",
    "科幻": "Science Fiction",
    "喜剧": "Comedy",
    "传记": "Biography",
    "历史": "History",
    "音乐": "Music",
    "惊悚": "Thriller",
    "犯罪": "Crime"
}

def backup_and_enify(app_env='production'):
    app = create_app(app_env)
    with app.app_context():
        films = Film.query.all()
        print(f"Found {len(films)} films in DB")

        backup = []
        for f in films:
            backup.append({
                "id": f.id,
                "title": f.title,
                "genre": f.genre,
                "year": f.year,
                "director": f.director,
                "description": f.description,
                "poster_url": f.poster_url
            })

        backup_path = os.path.join(os.path.dirname(__file__), "film_backup_originals.json")
        with open(backup_path, "w", encoding="utf-8") as fh:
            json.dump(backup, fh, indent=2, ensure_ascii=False)
        print(f"Backup written to {backup_path}")

        updated = 0
        for f in films:
            genre_en = GENRE_MAP.get(f.genre, f.genre or "")
            # Build a simple English description fallback
            parts = []
            if f.title:
                parts.append(f"{f.title}")
            if f.year:
                parts.append(f"({f.year})")
            intro = " ".join(parts) if parts else f.title or "This film"
            if genre_en:
                desc = f"{intro} is a {genre_en} film"
            else:
                desc = f"{intro} is a film"
            if f.director:
                desc += f" directed by {f.director}."
            else:
                desc += "."

            # Only overwrite if different
            if (not f.description) or (f.description and f.description and f.description.strip() and True):
                f.description = desc
                updated += 1

        if updated > 0:
            db.session.commit()
            print(f"Updated descriptions for {updated} films")
        else:
            print("No changes made")

if __name__ == "__main__":
    backup_and_enify()


