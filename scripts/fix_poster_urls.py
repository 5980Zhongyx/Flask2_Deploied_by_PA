#!/usr/bin/env python3
"""
Fix poster_url fields in database
Run on PythonAnywhere: python3 scripts/fix_poster_urls.py
"""
import os, sys

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def get_local_posters():
    """Get list of local poster files"""
    posters_dir = 'static/posters'
    if not os.path.exists(posters_dir):
        print(f"❌ posters directory not found: {posters_dir}")
        return []

    posters = [f for f in os.listdir(posters_dir) if f.lower().endswith('.jpg')]
    return sorted(posters)

def fix_poster_urls():
    """Reset poster_url based on film ID"""
    app = create_app('production')
    with app.app_context():
        from models.film import Film

        # Get local poster files
        local_posters = get_local_posters()
        print(f"Found {len(local_posters)} local poster files")

        # Get all films
        films = Film.query.order_by(Film.id).all()
        print(f"Database has {len(films)} films")

        # Set correct poster_url for each film
        updated = 0
        for i, film in enumerate(films):
            if i < len(local_posters):
                expected_filename = local_posters[i]
                if film.poster_url != expected_filename:
                    film.poster_url = expected_filename
                    updated += 1
                    print(f"Update {film.id}: {film.title[:20]}... -> {expected_filename}")
            else:
                print(f"⚠️  Film {film.id} has no corresponding poster file")

        if updated > 0:
            from app import db
            db.session.commit()
            print(f"\n✅ Successfully updated poster URLs for {updated} films")
        else:
            print("\nℹ️  All film poster URLs are already correct")

        # Show first 5 films' settings
        print("\nFirst 5 films' poster settings:")
        for film in films[:5]:
            status = "✓" if film.poster_url else "✗"
            print(f"  {status} {film.id}: {film.title[:20]}... -> {film.poster_url or 'None'}")

if __name__ == '__main__':
    print("🔧 Fix film poster URLs...\n")
    fix_poster_urls()
