#!/usr/bin/env python3
"""
Poster diagnostics script.
Run on PythonAnywhere: python3 scripts/check_posters.py
"""
import os
from app import create_app

def check_static_posters():
    """Get list of poster files in static/posters"""
    static_dir = 'static'
    posters_dir = os.path.join(static_dir, 'posters')

    if not os.path.exists(posters_dir):
        print(f"ERROR: static/posters directory not found: {posters_dir}")
        return []

    posters = [f for f in os.listdir(posters_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    posters = sorted(posters)
    print(f"Found {len(posters)} poster file(s) in static/posters/:")
    for poster in posters[:10]:
        print(f"  - {poster}")
    if len(posters) > 10:
        print(f"  ... and {len(posters) - 10} more")
    return posters

def check_database_posters(limit_show=10):
    """Inspect poster_url values in the database"""
    app = create_app('production')
    with app.app_context():
        from models.film import Film
        films = Film.query.all()
        print(f"\nDatabase has {len(films)} films")

        local_posters = 0
        remote_posters = 0
        no_posters = 0

        for film in films:
            if not film.poster_url:
                no_posters += 1
            elif film.poster_url.startswith(('http://', 'https://', '//')):
                remote_posters += 1
            else:
                local_posters += 1

        print(f"  - {local_posters} films reference local poster files")
        print(f"  - {remote_posters} films reference remote poster URLs")
        print(f"  - {no_posters} films have no poster_url")

        if local_posters > 0:
            print(f"\nFirst {limit_show} films with local poster filenames:")
            shown = 0
            for film in films:
                if film.poster_url and not film.poster_url.startswith(('http://', 'https://', '//')):
                    print(f"  {film.id}: {film.title[:50]} -> {film.poster_url}")
                    shown += 1
                    if shown >= limit_show:
                        break

def main():
    print("Poster diagnostics\n")

    static_posters = check_static_posters()
    check_database_posters(limit_show=10)

    print("\nDiagnosis summary:")
    if not static_posters:
        print("  - static/posters is empty or missing. Upload your poster files to that folder.")
    else:
        print("  - static/posters contains files.")
        print("  - If poster filenames are different from DB poster_url values, run scripts/map_posters_correctly.py or scripts/fix_poster_urls.py as appropriate.")

if __name__ == '__main__':
    main()
