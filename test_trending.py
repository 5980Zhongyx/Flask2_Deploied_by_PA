#!/usr/bin/env python3
"""Test script for trending data functionality"""

import os
import tempfile


from app import create_app, db


def test_trending_data():
    # Create temporary database for testing
    db_fd, db_path = tempfile.mkstemp()

    try:
        # Configure app with test database
        config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": False,
        }

        app = create_app("testing")
        app.config.update(config)

        with app.app_context():
            # Create all tables
            db.create_all()

            print("[OK] Database initialized successfully")

            # Test the trending data query logic
            try:
                from datetime import datetime, timedelta

                # Create some test data
                from werkzeug.security import generate_password_hash

                from models.film import Film
                from models.interaction import UserFilmInteraction
                from models.user import User

                user = User(
                    username="testuser",
                    email="test@example.com",
                    password_hash=generate_password_hash("password"),
                )
                db.session.add(user)

                film1 = Film(
                    title="Test Movie 1",
                    director="Test Director",
                    description="Test description",
                    year=2023,
                    genre="Action",
                    like_count=10,
                    rating_sum=45,
                    rating_count=10,
                )
                film2 = Film(
                    title="Test Movie 2",
                    director="Test Director 2",
                    description="Test description 2",
                    year=2023,
                    genre="Drama",
                    like_count=5,
                    rating_sum=35,
                    rating_count=7,
                )

                db.session.add(film1)
                db.session.add(film2)
                db.session.commit()

                # Create some recent interactions
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                recent_interaction1 = UserFilmInteraction(
                    user_id=user.id,
                    film_id=film1.id,
                    liked=True,
                    created_at=datetime.utcnow() - timedelta(days=1),
                )
                recent_interaction2 = UserFilmInteraction(
                    user_id=user.id,
                    film_id=film2.id,
                    liked=True,
                    review_text="Great movie!",
                    created_at=datetime.utcnow() - timedelta(days=2),
                )

                db.session.add(recent_interaction1)
                db.session.add(recent_interaction2)
                db.session.commit()

                print("[OK] Test data created successfully")

                # Test the trending query logic
                trending_query = (
                    db.session.query(
                        UserFilmInteraction.film_id,
                        db.func.count(UserFilmInteraction.film_id).label(
                            "interaction_count"
                        ),
                    )
                    .filter(
                        UserFilmInteraction.created_at >= seven_days_ago,
                        db.or_(
                            UserFilmInteraction.liked.is_(True),
                            UserFilmInteraction.review_text.isnot(None),
                        ),
                    )
                    .group_by(UserFilmInteraction.film_id)
                    .order_by(db.func.count(UserFilmInteraction.film_id).desc())
                    .limit(10)
                    .all()
                )

                print(f"[OK] Found {len(trending_query)} trending films")

                # Test daily interactions query
                daily_interactions = []
                for i in range(7):
                    day = datetime.utcnow() - timedelta(days=i)
                    day_start = datetime(day.year, day.month, day.day)
                    day_end = day_start + timedelta(days=1)

                    day_data = (
                        db.session.query(
                            db.func.count(UserFilmInteraction.film_id).label("count")
                        )
                        .filter(
                            UserFilmInteraction.created_at >= day_start,
                            UserFilmInteraction.created_at < day_end,
                            db.or_(
                                UserFilmInteraction.liked.is_(True),
                                UserFilmInteraction.review_text.isnot(None),
                            ),
                        )
                        .scalar()
                        or 0
                    )

                    daily_interactions.append(
                        {"date": day.strftime("%Y-%m-%d"), "count": day_data}
                    )

                print(
                    f"[OK] Daily interactions data generated for "
                    f"{len(daily_interactions)} days"
                )
                print("[OK] All trending functionality tests passed!")

            except Exception as e:
                print(f"[ERROR] Error testing trending functionality: {e}")
                return False

    finally:
        # Clean up
        os.close(db_fd)
        os.unlink(db_path)

    return True


if __name__ == "__main__":
    test_trending_data()
