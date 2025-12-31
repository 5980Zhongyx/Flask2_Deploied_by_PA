#!/usr/bin/env python3
import os
import sys

from app import create_app
from models.film import Film

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    env = os.environ.get("FLASK_ENV") or "production"
    app = create_app(env)
    with app.app_context():

        f = Film.query.order_by(Film.id).first()
        if not f:
            print("No films found")
            return
        print(f"Sample film: id={f.id}, title={f.title}")
        print("like_count:", getattr(f, "like_count", None))
        print("rating_count:", getattr(f, "rating_count", None))
        print("rating_sum:", getattr(f, "rating_sum", None))
        print("average_rating:", f.average_rating)


if __name__ == "__main__":
    main()
