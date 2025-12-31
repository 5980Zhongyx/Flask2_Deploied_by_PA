#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def main():
    env = os.environ.get('FLASK_ENV') or 'production'
    app = create_app(env)
    with app.app_context():
        from models.film import Film
        from models.interaction import UserFilmInteraction
        films = Film.query.all()
        print("Backfilling stats for", len(films), "films")
        for f in films:
            like_count = db.session.query(UserFilmInteraction).filter_by(film_id=f.id, liked=True).count()
            rating_sum = db.session.query(db.func.coalesce(db.func.sum(UserFilmInteraction.rating), 0)).filter(
                UserFilmInteraction.film_id == f.id, UserFilmInteraction.rating.isnot(None)
            ).scalar() or 0
            rating_count = db.session.query(UserFilmInteraction).filter(
                UserFilmInteraction.film_id == f.id, UserFilmInteraction.rating.isnot(None)
            ).count()
            f.like_count = int(like_count)
            f.rating_sum = int(rating_sum)
            f.rating_count = int(rating_count)
            db.session.add(f)
        db.session.commit()
        print("Backfill complete.")

if __name__ == '__main__':
    main()


