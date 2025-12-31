from flask import Blueprint, render_template, request, session, redirect, url_for
import os
import json
from flask_login import login_required, current_user
from app import db
from sqlalchemy import func

# Delayed import to avoid circular imports
from models.film import Film

film_bp = Blueprint("film", __name__)

@film_bp.route("/")
def index():
    films = Film.query.limit(12).all()
    liked_ids = set()
    if current_user.is_authenticated:
        from models.interaction import UserFilmInteraction
        liked = UserFilmInteraction.query.filter_by(user_id=current_user.id, liked=True).all()
        liked_ids = set(i.film_id for i in liked)
    return render_template("index.html", films=films, liked_ids=liked_ids)

@film_bp.route("/films")
def list_films():
    # Restore search/filter/sort functionality (likes/rating sorting done in memory for model property compatibility)
    page = int(request.args.get('page', 1))
    per_page = 12
    search = request.args.get('search', '').strip()
    genre = request.args.get('genre', '').strip()
    year = request.args.get('year', '').strip()
    sort_by = request.args.get('sort', 'title')

    # Build base query (only filtering, no property-based sorting here)
    query = Film.query
    if search:
        query = query.filter(
            (Film.title.contains(search)) |
            (Film.director.contains(search)) |
            (Film.description.contains(search))
        )
    if genre:
        query = query.filter(Film.genre.contains(genre))
    if year:
        try:
            y = int(year)
            query = query.filter(Film.year == y)
        except ValueError:
            pass

    # If sorting by likes/rating/year/title, sort at SQL level (using persistent fields)
    if sort_by == 'likes':
        query = query.order_by(Film.like_count.desc(), Film.title)
    elif sort_by == 'rating':
        # Calculate persistent average: rating_sum / rating_count (prevent division by zero)
        avg_expr = func.coalesce((Film.rating_sum * 1.0) / func.nullif(Film.rating_count, 0), 0)
        query = query.order_by(avg_expr.desc(), Film.like_count.desc(), Film.title)
    elif sort_by == 'year':
        query = query.order_by(Film.year.desc(), Film.title)
    else:
        query = query.order_by(Film.title)

    total = query.count()
    films = query.offset((page - 1) * per_page).limit(per_page).all()

    # get filter options
    genres_q = db.session.query(Film.genre).distinct().all()
    genres = [g[0] for g in genres_q if g[0]]
    years_q = db.session.query(Film.year).distinct().filter(Film.year.isnot(None)).all()
    years = sorted([y[0] for y in years_q if y[0]], reverse=True)

    liked_ids = set()
    if current_user.is_authenticated:
        from models.interaction import UserFilmInteraction
        liked = UserFilmInteraction.query.filter_by(user_id=current_user.id, liked=True).all()
        liked_ids = set(i.film_id for i in liked)

    return render_template("film_list.html",
                         films=films,
                         liked_ids=liked_ids,
                         page=page,
                         per_page=per_page,
                         total=total)

@film_bp.route("/films/<int:film_id>")
def film_detail(film_id):
    from models.interaction import UserFilmInteraction

    film = Film.query.get_or_404(film_id)

    # get user interaction information
    user_interaction = None
    if current_user.is_authenticated:
        user_interaction = UserFilmInteraction.query.filter_by(
            user_id=current_user.id, film_id=film_id
        ).first()

    # get other users' comments (with text)
    reviews = UserFilmInteraction.query.filter(
        UserFilmInteraction.film_id == film_id,
        UserFilmInteraction.review_text.isnot(None),
        UserFilmInteraction.review_text != ''
    ).order_by(UserFilmInteraction.created_at.desc()).all()

    return render_template("film_detail.html",
                         film=film,
                         user_interaction=user_interaction,
                         reviews=reviews)

@film_bp.route("/recommendations")
@login_required
def recommendations():
    from models.interaction import UserFilmInteraction
    from datetime import datetime, timedelta

    # For now replace complex recommenders with popularity-based lists:
    # - most_liked: films ordered by like_count desc
    # - highest_rated: films ordered by persisted rating_sum/rating_count desc (safe SQL expression)
    # - recent: recently added films
    most_liked = Film.query.order_by(Film.like_count.desc(), Film.title).limit(12).all()
    avg_expr = func.coalesce((Film.rating_sum * 1.0) / func.nullif(Film.rating_count, 0), 0)
    highest_rated = Film.query.order_by(avg_expr.desc(), Film.title).limit(12).all()
    recent = Film.query.order_by(Film.created_at.desc()).limit(12).all()

    # Calculate trending/hot films based on recent interactions (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Get top 10 films by recent interactions (likes + reviews) in the last 7 days
    trending_query = db.session.query(
        UserFilmInteraction.film_id,
        func.count(UserFilmInteraction.film_id).label('interaction_count')
    ).filter(
        UserFilmInteraction.created_at >= seven_days_ago,
        db.or_(UserFilmInteraction.liked == True, UserFilmInteraction.review_text.isnot(None))
    ).group_by(UserFilmInteraction.film_id).order_by(func.count(UserFilmInteraction.film_id).desc()).limit(10).all()

    # Get film details for trending films
    trending_film_ids = [t.film_id for t in trending_query]
    trending_films = Film.query.filter(Film.id.in_(trending_film_ids)).all()

    # Create trending data with film info
    trending_data = []
    for film in trending_films:
        interaction_count = next((t.interaction_count for t in trending_query if t.film_id == film.id), 0)
        trending_data.append({
            'film': film,
            'interaction_count': interaction_count
        })

    # Sort by interaction count
    trending_data.sort(key=lambda x: x['interaction_count'], reverse=True)

    # Get daily interaction data for the last 7 days for trending chart
    daily_interactions = []
    for i in range(7):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)

        day_data = db.session.query(
            func.count(UserFilmInteraction.film_id).label('count')
        ).filter(
            UserFilmInteraction.created_at >= day_start,
            UserFilmInteraction.created_at < day_end,
            db.or_(UserFilmInteraction.liked == True, UserFilmInteraction.review_text.isnot(None))
        ).scalar() or 0

        daily_interactions.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': day_data
        })

    # Reverse to show oldest to newest
    daily_interactions.reverse()

    # Minimal stats for the page
    recommendation_data = {
        'user_interactions_count': 0,
        'total_users': db.session.query(func.count()).select_from(db.text('user')).scalar() if False else 0,
        'recommendations': []
    }

    return render_template("recommendations.html",
                           most_liked=most_liked,
                           highest_rated=highest_rated,
                           recent=recent,
                           trending_data=trending_data,
                           daily_interactions=daily_interactions,
                           recommendation_data=recommendation_data)

@film_bp.route('/language/<lang>')
def set_language(lang):
    """Set the language for the session"""
    if lang in ['en', 'zh']:
        session['language'] = lang
    # Return a JSON response so AJAX callers receive the Set-Cookie header reliably.
    from flask import jsonify
    return jsonify({"status": "ok", "language": lang})
