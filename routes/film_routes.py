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
    from models.recommendation import recommendation_engine
    # get user's personalized recommendations (existing user-based collaborative filtering)
    recommendation_data = recommendation_engine.get_user_recommendations(current_user.id, top_n=10)

    # get advanced recommendations (item-based and matrix factorization)
    try:
        from models.recommendation_advanced import item_recommender, mf_recommender
        item_recs = item_recommender.recommend(current_user.id, top_n=10)
        mf_recs = mf_recommender.recommend(current_user.id, top_n=10)
    except Exception:
        item_recs = []
        mf_recs = []

    # read evaluation results (if exists)
    eval_metrics = None
    eval_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'recommendation_eval.json')
    if os.path.exists(eval_path):
        try:
            with open(eval_path, 'r', encoding='utf-8') as f:
                eval_metrics = json.load(f)
        except Exception:
            eval_metrics = None
    return render_template("recommendations.html",
                           recommendation_data=recommendation_data,
                           item_recs=item_recs,
                           mf_recs=mf_recs,
                           eval_metrics=eval_metrics)

@film_bp.route('/language/<lang>')
def set_language(lang):
    """Set the language for the session"""
    if lang in ['en', 'zh']:
        session['language'] = lang
    # Return a JSON response so AJAX callers receive the Set-Cookie header reliably.
    from flask import jsonify
    return jsonify({"status": "ok", "language": lang})
