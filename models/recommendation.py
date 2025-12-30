"""
推荐系统模块
基于用户共同偏好的协同过滤推荐
"""

from collections import defaultdict
from typing import List, Dict, Tuple
from app import db
from .user import User
from .film import Film
from .interaction import UserFilmInteraction


class RecommendationEngine:
    """推荐引擎类"""

    def __init__(self):
        self.user_interactions = {}  # 用户 -> 电影偏好映射
        self.film_interactions = {}  # 电影 -> 用户映射
        self._load_data()

    def _load_data(self):
        """加载所有用户交互数据"""
        interactions = UserFilmInteraction.query.all()

        for interaction in interactions:
            user_id = interaction.user_id
            film_id = interaction.film_id

            # 初始化用户偏好字典
            if user_id not in self.user_interactions:
                self.user_interactions[user_id] = {}

            # 计算用户对电影的偏好分数 (0-5分)
            preference_score = 0
            if interaction.liked:
                preference_score += 3  # 点赞加3分
            if interaction.rating:
                preference_score += interaction.rating  # 评分直接加分
            if interaction.has_review:
                preference_score += 1  # 评论加1分

            self.user_interactions[user_id][film_id] = preference_score

            # 初始化电影用户映射
            if film_id not in self.film_interactions:
                self.film_interactions[film_id] = set()
            self.film_interactions[film_id].add(user_id)

    def get_similar_users(self, user_id: int, top_n: int = 10) -> List[Tuple[int, float]]:
        """
        找到与指定用户最相似的其他用户
        返回: [(user_id, similarity_score), ...]
        """
        if user_id not in self.user_interactions:
            return []

        target_user_films = self.user_interactions[user_id]
        similarities = []

        for other_user_id, other_user_films in self.user_interactions.items():
            if other_user_id == user_id:
                continue

            # 计算余弦相似度
            similarity = self._calculate_cosine_similarity(target_user_films, other_user_films)
            if similarity > 0:  # 只保留正相关用户
                similarities.append((other_user_id, similarity))

        # 按相似度排序，返回前top_n个
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    def _calculate_cosine_similarity(self, user1_films: Dict[int, int], user2_films: Dict[int, int]) -> float:
        """计算两个用户的余弦相似度"""
        # 获取共同评价的电影
        common_films = set(user1_films.keys()) & set(user2_films.keys())

        if not common_films:
            return 0.0

        # 计算向量点积
        dot_product = sum(user1_films[film] * user2_films[film] for film in common_films)

        # 计算向量长度
        user1_norm = sum(score ** 2 for score in user1_films.values()) ** 0.5
        user2_norm = sum(score ** 2 for score in user2_films.values()) ** 0.5

        if user1_norm == 0 or user2_norm == 0:
            return 0.0

        return dot_product / (user1_norm * user2_norm)

    def recommend_films(self, user_id: int, top_n: int = 10) -> List[Tuple[Film, float]]:
        """
        为用户推荐电影
        返回: [(Film对象, 推荐分数), ...]
        """
        if user_id not in self.user_interactions:
            # 新用户，返回热门电影
            return self._get_popular_films(top_n)

        # 获取用户已交互的电影
        interacted_films = set(self.user_interactions[user_id].keys())

        # 获取相似用户
        similar_users = self.get_similar_users(user_id, top_n=20)

        if not similar_users:
            # 没有相似用户，返回热门电影
            return self._get_popular_films(top_n)

        # 收集推荐候选
        recommendations = defaultdict(float)
        total_similarity = 0

        for similar_user_id, similarity in similar_users:
            similar_user_films = self.user_interactions[similar_user_id]

            for film_id, score in similar_user_films.items():
                if film_id not in interacted_films and score > 0:
                    # 加权推荐分数
                    recommendations[film_id] += similarity * score
                    total_similarity += similarity

        if not recommendations:
            return self._get_popular_films(top_n)

        # 标准化推荐分数并排序
        normalized_recommendations = []
        for film_id, score in recommendations.items():
            normalized_score = score / total_similarity if total_similarity > 0 else 0
            normalized_recommendations.append((film_id, normalized_score))

        normalized_recommendations.sort(key=lambda x: x[1], reverse=True)

        # 获取电影对象并返回前top_n个
        result = []
        for film_id, score in normalized_recommendations[:top_n]:
            film = Film.query.get(film_id)
            if film:
                result.append((film, score))

        return result

    def _get_popular_films(self, top_n: int = 10) -> List[Tuple[Film, float]]:
        """获取热门电影作为备选推荐"""
        popular_films = Film.query.order_by(db.desc(Film.like_count)).limit(top_n).all()
        return [(film, film.like_count / 100.0) for film in popular_films]  # 标准化分数

    def get_user_recommendations(self, user_id: int, top_n: int = 10) -> Dict:
        """
        获取用户的完整推荐信息，包括相似用户和推荐理由
        """
        recommendations = self.recommend_films(user_id, top_n)

        # 获取相似用户的信息
        similar_users = self.get_similar_users(user_id, top_n=5)
        similar_user_objects = []
        for sim_user_id, similarity in similar_users:
            user = User.query.get(sim_user_id)
            if user:
                similar_user_objects.append({
                    'user': user,
                    'similarity': similarity,
                    'common_interactions': len(set(self.user_interactions[user_id].keys()) &
                                             set(self.user_interactions[sim_user_id].keys()))
                })

        return {
            'recommendations': recommendations,
            'similar_users': similar_user_objects,
            'total_users': len(self.user_interactions),
            'user_interactions_count': len(self.user_interactions.get(user_id, {}))
        }


# 全局推荐引擎实例
recommendation_engine = RecommendationEngine()
