from datetime import datetime
from app import db

class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.Integer)
    director = db.Column(db.String(100))
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系定义
    interactions = db.relationship('UserFilmInteraction', backref='film', lazy=True)

    def __repr__(self):
        return f'<Film {self.title}>'

    @property
    def average_rating(self):
        """计算平均评分"""
        ratings = [interaction.rating for interaction in self.interactions if interaction.rating]
        return sum(ratings) / len(ratings) if ratings else 0

    @property
    def like_count(self):
        """计算点赞数量"""
        return sum(1 for interaction in self.interactions if interaction.liked)
