from flask import Blueprint, render_template, request
import os
import json
from flask_login import login_required, current_user
from app import db
from sqlalchemy import func

# 延迟导入以避免循环导入
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
    # 恢复搜索/筛选/排序功能（为了兼容 model 中的 property，likes/rating 排序在内存中完成）
    page = int(request.args.get('page', 1))
    per_page = 12
    search = request.args.get('search', '').strip()
    genre = request.args.get('genre', '').strip()
    year = request.args.get('year', '').strip()
    sort_by = request.args.get('sort', 'title')

    # 构建基础查询（只做过滤，不在这里做基于 property 的排序）
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

    films_all = query.all()

    # 支持按 likes / rating 的排序（这些通常是 property，不能用于 SQL order_by，因此在 Python 中排序）
    if sort_by == 'year':
        films_all.sort(key=lambda f: f.year or 0, reverse=True)
    elif sort_by == 'rating':
        films_all.sort(key=lambda f: getattr(f, 'average_rating', 0) or 0, reverse=True)
    elif sort_by == 'likes':
        films_all.sort(key=lambda f: getattr(f, 'like_count', 0) or 0, reverse=True)
    else:
        films_all.sort(key=lambda f: (f.title or '').lower())

    total = len(films_all)
    start = (page - 1) * per_page
    end = start + per_page
    films = films_all[start:end]

    # 获取筛选选项
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

    # 获取用户交互信息
    user_interaction = None
    if current_user.is_authenticated:
        user_interaction = UserFilmInteraction.query.filter_by(
            user_id=current_user.id, film_id=film_id
        ).first()

    # 获取其他用户的评论（有评论文本的）
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
    # 获取用户的个性化推荐（现有用户基于用户的协同过滤）
    recommendation_data = recommendation_engine.get_user_recommendations(current_user.id, top_n=10)

    # 获取高级推荐（item-based 与 matrix factorization）
    try:
        from models.recommendation_advanced import item_recommender, mf_recommender
        item_recs = item_recommender.recommend(current_user.id, top_n=10)
        mf_recs = mf_recommender.recommend(current_user.id, top_n=10)
    except Exception:
        item_recs = []
        mf_recs = []

    # 读取评估结果（若存在）
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
