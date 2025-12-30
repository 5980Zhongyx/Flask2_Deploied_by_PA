from flask import Blueprint, render_template, request
import os
import json
from flask_login import login_required, current_user
from app import db

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
    # 获取查询参数
    search = request.args.get('search', '')
    genre = request.args.get('genre', '')
    year = request.args.get('year', '')
    sort_by = request.args.get('sort', 'title')
    page = int(request.args.get('page', 1))
    per_page = 12

    # 构建查询
    query = Film.query

    # 搜索过滤
    if search:
        query = query.filter(
            (Film.title.contains(search)) |
            (Film.director.contains(search)) |
            (Film.description.contains(search))
        )

    # 类型过滤
    if genre:
        query = query.filter(Film.genre.contains(genre))

    # 年份过滤
    if year:
        query = query.filter(Film.year == int(year))

    # 排序
    if sort_by == 'year':
        query = query.order_by(Film.year.desc())
    elif sort_by == 'rating':
        query = query.order_by(Film.average_rating.desc())
    elif sort_by == 'likes':
        query = query.order_by(Film.like_count.desc())
    else:  # 默认按标题排序
        query = query.order_by(Film.title)

    # 分页
    total = query.count()
    films = query.offset((page - 1) * per_page).limit(per_page).all()

    # 获取筛选选项
    genres = db.session.query(Film.genre).distinct().all()
    genres = [g[0] for g in genres if g[0]]

    years = db.session.query(Film.year).distinct().filter(Film.year.isnot(None)).all()
    years = sorted([y[0] for y in years if y[0]], reverse=True)

    liked_ids = set()
    if current_user.is_authenticated:
        from models.interaction import UserFilmInteraction
        liked = UserFilmInteraction.query.filter_by(user_id=current_user.id, liked=True).all()
        liked_ids = set(i.film_id for i in liked)

    return render_template("film_list.html",
                         films=films,
                         liked_ids=liked_ids,
                         search=search,
                         genre=genre,
                         year=year,
                         sort_by=sort_by,
                         page=page,
                         per_page=per_page,
                         total=total,
                         genres=genres,
                         years=years)

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
