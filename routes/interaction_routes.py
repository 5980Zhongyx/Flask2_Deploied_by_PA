import logging
from flask import Blueprint, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models import UserFilmInteraction, Film

interaction_bp = Blueprint("interaction", __name__)

# 配置日志
interaction_logger = logging.getLogger('interaction')

@interaction_bp.route("/api/interaction/<int:film_id>", methods=["POST", "PUT", "DELETE"])
@login_required
def handle_interaction(film_id):
    """处理用户与电影的交互（点赞、评分、评论）"""
    film = Film.query.get_or_404(film_id)

    # 获取或创建交互记录
    interaction = UserFilmInteraction.query.filter_by(
        user_id=current_user.id, film_id=film_id
    ).first()

    if request.method == "DELETE":
        # 删除交互
        if interaction:
            db.session.delete(interaction)
            db.session.commit()
            interaction_logger.info(f"Interaction deleted: User {current_user.username} - Film {film.title}")
            return jsonify({"success": True, "message": "评价已删除"})
        return jsonify({"success": False, "message": "未找到评价记录"}), 404

    # POST/PUT: 创建或更新交互
    data = request.get_json() if request.is_json else request.form

    liked = data.get('liked', False)
    rating = data.get('rating')
    review_text = data.get('review', '').strip()

    # 转换数据类型
    if isinstance(liked, str):
        liked = liked.lower() in ('true', '1', 'yes', 'on')
    if isinstance(rating, str) and rating:
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                rating = None
        except ValueError:
            rating = None
    elif not rating:
        rating = None

    if not interaction:
        # 创建新交互
        interaction = UserFilmInteraction(
            user_id=current_user.id,
            film_id=film_id,
            liked=liked,
            rating=rating,
            review_text=review_text if review_text else None
        )
        db.session.add(interaction)
        action = "created"
    else:
        # 更新现有交互
        interaction.liked = liked
        interaction.rating = rating
        interaction.review_text = review_text if review_text else None
        action = "updated"

    try:
        db.session.commit()
        interaction_logger.info(f"Interaction {action}: User {current_user.username} - Film {film.title} - Liked: {liked}, Rating: {rating}")

        # 返回更新后的统计数据
        film.refresh()  # 刷新电影对象以获取最新统计
        return jsonify({
            "success": True,
            "message": "评价已保存",
            "data": {
                "liked": interaction.liked,
                "rating": interaction.rating,
                "has_review": interaction.has_review,
                "review_text": interaction.review_text,
                "created_at": interaction.created_at.isoformat() if interaction.created_at else None,
                "film_stats": {
                    "average_rating": film.average_rating,
                    "like_count": film.like_count,
                    "rating_count": len([i for i in film.interactions if i.rating])
                }
            }
        })
    except Exception as e:
        db.session.rollback()
        interaction_logger.error(f"Interaction save failed: User {current_user.username} - Film {film.title} - Error: {str(e)}")
        return jsonify({"success": False, "message": "保存失败，请重试"}), 500

@interaction_bp.route("/api/like/<int:film_id>", methods=["POST"])
@login_required
def toggle_like(film_id):
    """AJAX点赞/取消点赞"""
    film = Film.query.get_or_404(film_id)

    interaction = UserFilmInteraction.query.filter_by(
        user_id=current_user.id, film_id=film_id
    ).first()

    if not interaction:
        # 创建新交互，只设置点赞
        interaction = UserFilmInteraction(
            user_id=current_user.id,
            film_id=film_id,
            liked=True
        )
        db.session.add(interaction)
    else:
        # 切换点赞状态
        interaction.liked = not interaction.liked

    try:
        db.session.commit()
        film.refresh()  # 刷新统计数据

        action = "liked" if interaction.liked else "unliked"
        interaction_logger.info(f"Film {action}: User {current_user.username} - Film {film.title}")

        return jsonify({
            "success": True,
            "liked": interaction.liked,
            "like_count": film.like_count,
            "message": f"已{'点赞' if interaction.liked else '取消点赞'}"
        })
    except Exception as e:
        db.session.rollback()
        interaction_logger.error(f"Like toggle failed: User {current_user.username} - Film {film.title} - Error: {str(e)}")
        return jsonify({"success": False, "message": "操作失败，请重试"}), 500

# 保持向后兼容的路由
@interaction_bp.route("/like/<int:film_id>", methods=["POST"])
@login_required
def like_film(film_id):
    """传统点赞路由，重定向到详情页"""
    film = Film.query.get_or_404(film_id)

    interaction = UserFilmInteraction.query.filter_by(
        user_id=current_user.id, film_id=film_id
    ).first()

    if not interaction:
        interaction = UserFilmInteraction(
            user_id=current_user.id,
            film_id=film_id,
            liked=True
        )
        db.session.add(interaction)
    else:
        interaction.liked = not interaction.liked

    db.session.commit()
    film.refresh()

    action = "liked" if interaction.liked else "unliked"
    interaction_logger.info(f"Film {action}: User {current_user.username} - Film {film.title}")

    flash(f"已{'点赞' if interaction.liked else '取消点赞'}", "success")
    return redirect(url_for('film.film_detail', film_id=film_id))
