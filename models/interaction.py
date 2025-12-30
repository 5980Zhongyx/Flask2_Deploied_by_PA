from datetime import datetime
from app import db

class UserFilmInteraction(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey("film.id"), primary_key=True)

    liked = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5分
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Interaction User:{self.user_id} Film:{self.film_id}>'

    @property
    def has_review(self):
        """检查是否有评论"""
        return self.review_text is not None and self.review_text.strip() != ""
