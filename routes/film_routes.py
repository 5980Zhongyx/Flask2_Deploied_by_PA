from flask import Blueprint, render_template, request
from app import db

# 延迟导入以避免循环导入
from models.film import Film

film_bp = Blueprint("film", __name__)

@film_bp.route("/")
def index():
    films = Film.query.limit(12).all()
    return render_template("index.html", films=films)

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

    return render_template("film_list.html",
                         films=films,
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
    film = Film.query.get_or_404(film_id)
    return render_template("film_detail.html", film=film)

@film_bp.route("/recommendations")
def recommendations():
    # 简单的推荐逻辑：返回评分最高的电影
    films = Film.query.order_by(Film.average_rating.desc()).limit(10).all()
    return render_template("recommendations.html", films=films)
