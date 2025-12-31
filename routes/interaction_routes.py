import logging

from flask import Blueprint, flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required

from app import db
from models.film import Film
from models.interaction import UserFilmInteraction

interaction_bp = Blueprint("interaction", __name__)

# configure logging
interaction_logger = logging.getLogger("interaction")


@interaction_bp.route(
    "/api/interaction/<int:film_id>", methods=["POST", "PUT", "DELETE"]
)
@login_required
def handle_interaction(film_id):
    """handle user-film interactions (like, rating, comment)"""
    film = Film.query.get_or_404(film_id)

    # get or create interaction record
    interaction = UserFilmInteraction.query.filter_by(
        user_id=current_user.id, film_id=film_id
    ).first()

    if request.method == "DELETE":
        # delete interaction
        if interaction:
            # adjust persisted film stats
            try:
                if interaction.liked:
                    film.like_count = max(0, (film.like_count or 0) - 1)
                if interaction.rating:
                    film.rating_count = max(0, (film.rating_count or 0) - 1)
                    film.rating_sum = max(
                        0, (film.rating_sum or 0) - (interaction.rating or 0)
                    )
                db.session.delete(interaction)
                db.session.add(film)
                db.session.commit()
                interaction_logger.info(
                    f"Interaction deleted: User {current_user.username} - "
                    f"Film {film.title}"
                )
                return jsonify({"success": True, "message": "评价已删除"})
            except Exception as e:
                db.session.rollback()
                interaction_logger.error(f"Failed to delete interaction: {e}")
                return jsonify({"success": False, "message": "删除失败"}), 500
        return jsonify({"success": False, "message": "未找到评价记录"}), 404

    # POST/PUT: create or update interaction
    data = request.get_json() if request.is_json else request.form

    liked = data.get("liked", False)
    rating = data.get("rating")
    review_text = data.get("review", "").strip()

    # convert data type
    if isinstance(liked, str):
        liked = liked.lower() in ("true", "1", "yes", "on")
    if isinstance(rating, str) and rating:
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                rating = None
        except ValueError:
            rating = None
    elif not rating:
        rating = None

    # handle create or update with persisted counters
    prev_liked = None
    prev_rating = None
    if not interaction:
        # create new interaction
        interaction = UserFilmInteraction(
            user_id=current_user.id,
            film_id=film_id,
            liked=liked,
            rating=rating,
            review_text=review_text if review_text else None,
        )
        db.session.add(interaction)
        prev_liked = None
        prev_rating = None
        action = "created"
    else:
        prev_liked = interaction.liked
        prev_rating = interaction.rating
        # update existing interaction
        interaction.liked = liked
        interaction.rating = rating
        interaction.review_text = review_text if review_text else None
        action = "updated"

    # adjust film persisted stats based on diff
    try:
        # liked diff
        if prev_liked is None:
            if liked:
                film.like_count = (film.like_count or 0) + 1
        else:
            if prev_liked != bool(liked):
                if liked:
                    film.like_count = (film.like_count or 0) + 1
                else:
                    film.like_count = max(0, (film.like_count or 0) - 1)

        # rating diff
        if prev_rating is None and rating is not None:
            film.rating_count = (film.rating_count or 0) + 1
            film.rating_sum = (film.rating_sum or 0) + (rating or 0)
        elif prev_rating is not None and rating is None:
            film.rating_count = max(0, (film.rating_count or 0) - 1)
            film.rating_sum = max(0, (film.rating_sum or 0) - (prev_rating or 0))
        elif prev_rating is not None and rating is not None and prev_rating != rating:
            film.rating_sum = (film.rating_sum or 0) + (rating - prev_rating)

        db.session.add(film)
        db.session.commit()
        interaction_logger.info(
            f"Interaction {action}: User {current_user.username} - "
            f"Film {film.title} - Liked: {liked}, Rating: {rating}"
        )

        # return updated statistics
        # refresh film object to get latest statistics
        db.session.refresh(film)
        return jsonify(
            {
                "success": True,
                "message": "Rating saved",
                "data": {
                    "liked": interaction.liked,
                    "rating": interaction.rating,
                    "has_review": interaction.has_review,
                    "review_text": interaction.review_text,
                    "created_at": (
                        interaction.created_at.isoformat()
                        if interaction.created_at
                        else None
                    ),
                    "film_stats": {
                        "average_rating": film.average_rating,
                        "like_count": film.like_count,
                        "rating_count": film.rating_count,
                    },
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        interaction_logger.error(
            f"Interaction save failed: User {current_user.username} - "
            f"Film {film.title} - Error: {str(e)}"
        )
        return (
            jsonify({"success": False, "message": "Save failed, please try again"}),
            500,
        )


@interaction_bp.route("/api/reviews/<int:film_id>", methods=["GET"])
def get_reviews(film_id):
    """Paginate comments for specified film (only with text),
    used for frontend no refresh loading."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 5))

    reviews_query = UserFilmInteraction.query.filter(
        UserFilmInteraction.film_id == film_id,
        UserFilmInteraction.review_text.isnot(None),
        UserFilmInteraction.review_text != "",
    ).order_by(UserFilmInteraction.created_at.desc())

    total = reviews_query.count()
    reviews = reviews_query.offset((page - 1) * per_page).limit(per_page).all()

    results = []
    for r in reviews:
        # UserFilmInteraction uses composite PK, no single 'id' field.
        composite_id = f"{r.user_id}-{r.film_id}"
        composite_id = f"{r.user_id}-{r.film_id}"
        results.append(
            {
                "id": composite_id,
                "user": {
                    "id": r.user_id,
                    "username": getattr(r.user, "username", None),
                },
                "rating": r.rating,
                "review_text": r.review_text,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
        )

    return jsonify(
        {
            "success": True,
            "data": results,
            "page": page,
            "per_page": per_page,
            "total": total,
        }
    )


@interaction_bp.route("/api/like/<int:film_id>", methods=["POST"])
@login_required
def toggle_like(film_id):
    """AJAX like/unlike"""
    film = Film.query.get_or_404(film_id)

    interaction = UserFilmInteraction.query.filter_by(
        user_id=current_user.id, film_id=film_id
    ).first()

    if not interaction:
        # create new interaction, only set like
        interaction = UserFilmInteraction(
            user_id=current_user.id, film_id=film_id, liked=True
        )
        db.session.add(interaction)
        # increment persisted like count
        film.like_count = (film.like_count or 0) + 1
    else:
        # toggle like status
        prev = interaction.liked
        interaction.liked = not interaction.liked
        # adjust persisted like count
        if prev != interaction.liked:
            if interaction.liked:
                film.like_count = (film.like_count or 0) + 1
            else:
                film.like_count = max(0, (film.like_count or 0) - 1)

    try:
        db.session.add(film)
        db.session.commit()
        # refresh statistics
        db.session.refresh(film)

        action = "liked" if interaction.liked else "unliked"
        interaction_logger.info(
            f"Film {action}: User {current_user.username} - Film {film.title}"
        )

        return jsonify(
            {
                "success": True,
                "liked": interaction.liked,
                "like_count": film.like_count,
                "message": f"{'Liked' if interaction.liked else 'Unliked'}",
            }
        )
    except Exception as e:
        db.session.rollback()
        interaction_logger.error(
            f"Like toggle failed: User {current_user.username} - "
            f"Film {film.title} - Error: {str(e)}"
        )
        return (
            jsonify(
                {"success": False, "message": "Operation failed, please try again"}
            ),
            500,
        )


# keep backward compatibility route
@interaction_bp.route("/like/<int:film_id>", methods=["POST"])
@login_required
def like_film(film_id):
    """traditional like route, redirect to detail page"""
    film = Film.query.get_or_404(film_id)

    interaction = UserFilmInteraction.query.filter_by(
        user_id=current_user.id, film_id=film_id
    ).first()

    if not interaction:
        interaction = UserFilmInteraction(
            user_id=current_user.id, film_id=film_id, liked=True
        )
        db.session.add(interaction)
        film.like_count = (film.like_count or 0) + 1
    else:
        prev = interaction.liked
        interaction.liked = not interaction.liked
        if prev != interaction.liked:
            if interaction.liked:
                film.like_count = (film.like_count or 0) + 1
            else:
                film.like_count = max(0, (film.like_count or 0) - 1)

    db.session.add(film)
    db.session.commit()
    db.session.refresh(film)

    action = "liked" if interaction.liked else "unliked"
    interaction_logger.info(
        f"Film {action}: User {current_user.username} - Film {film.title}"
    )

    flash(f"{'Liked' if interaction.liked else 'Unliked'}", "success")
    return redirect(url_for("film.film_detail", film_id=film_id))
