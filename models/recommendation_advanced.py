"""
高级推荐模块：实现 item-based 协同过滤 与 简单的矩阵分解(基于 numpy 的 FunkSVD)
接口与返回与现有 recommendation_engine 兼容：返回 [(Film, score), ...]
"""
from collections import defaultdict
from typing import List, Tuple
from app import db
from .film import Film
from .interaction import UserFilmInteraction

try:
    import numpy as np
except Exception:
    np = None
import os
import json

MODEL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'recommendation_mf.npz')


class ItemBasedRecommender:
    def __init__(self):
        self._load_data()

    def _load_data(self):
        # user -> {film:score}
        self.user_interactions = defaultdict(dict)
        interactions = UserFilmInteraction.query.all()
        for it in interactions:
            score = 0
            if it.liked:
                score += 3
            if it.rating:
                score += it.rating
            if it.has_review:
                score += 1
            if score <= 0:
                continue
            self.user_interactions[it.user_id][it.film_id] = score

        # build item->users
        self.item_users = defaultdict(set)
        for u, films in self.user_interactions.items():
            for f in films:
                self.item_users[f].add(u)

        # compute item-item similarity (Jaccard on users)
        self.similarity = defaultdict(dict)
        items = list(self.item_users.keys())
        for i in range(len(items)):
            a = items[i]
            users_a = self.item_users[a]
            for j in range(i+1, len(items)):
                b = items[j]
                users_b = self.item_users[b]
                inter = users_a & users_b
                union = users_a | users_b
                if not union:
                    sim = 0.0
                else:
                    sim = len(inter) / len(union)
                self.similarity[a][b] = sim
                self.similarity[b][a] = sim

    def recommend(self, user_id: int, top_n=10):
        if user_id not in self.user_interactions:
            # fallback popularity
            films = Film.query.order_by(db.desc(Film.like_count)).limit(top_n).all()
            return [(f, f.like_count/100.0) for f in films]

        interacted = set(self.user_interactions[user_id].keys())
        scores = defaultdict(float)
        for item in interacted:
            for other, sim in self.similarity.get(item, {}).items():
                if other in interacted: continue
                scores[other] += sim * self.user_interactions[user_id].get(item, 0)

        if not scores:
            films = Film.query.order_by(db.desc(Film.like_count)).limit(top_n).all()
            return [(f, f.like_count/100.0) for f in films]

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result = []
        for fid, sc in ranked:
            film = Film.query.get(fid)
            if film:
                result.append((film, sc))
        return result


class MatrixFactorizationRecommender:
    def __init__(self, factors=10, epochs=20, lr=0.01, reg=0.02):
        self.factors = factors
        self.epochs = epochs
        self.lr = lr
        self.reg = reg
        self.user_map = {}
        self.item_map = {}
        self.P = None
        self.Q = None
        self._trained = False
        self._load_and_train()

    def _load_and_train(self):
        # try to load persisted model first
        if self._try_load_model():
            return

        if np is None:
            # numpy not available; skip training
            self._trained = False
            return

        interactions = UserFilmInteraction.query.all()
        # build ids
        users = sorted({it.user_id for it in interactions})
        items = sorted({it.film_id for it in interactions})
        self.user_map = {u:i for i,u in enumerate(users)}
        self.item_map = {i:j for j,i in enumerate(items)}

        # build matrix as dict of (u,i)->score
        data = []
        for it in interactions:
            score = 0
            if it.liked: score += 3
            if it.rating: score += it.rating
            if it.has_review: score += 1
            if score <= 0: continue
            data.append((self.user_map[it.user_id], self.item_map[it.film_id], score))

        if not data:
            self._trained = False
            return

        num_users = len(self.user_map)
        num_items = len(self.item_map)
        k = self.factors
        # initialize P,Q
        self.P = np.random.normal(scale=0.1, size=(num_users, k))
        self.Q = np.random.normal(scale=0.1, size=(num_items, k))

        for epoch in range(self.epochs):
            for (u,i,r) in data:
                pred = self.P[u].dot(self.Q[i])
                e = r - pred
                self.P[u] += self.lr * (e * self.Q[i] - self.reg * self.P[u])
                self.Q[i] += self.lr * (e * self.P[u] - self.reg * self.Q[i])
        self._trained = True
        # save model to disk
        try:
            self._save_model()
        except Exception:
            pass

    def _save_model(self):
        """保存 P/Q 矩阵与映射到文件，以便下次加载"""
        os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
        np.savez(MODEL_FILE,
                 P=self.P,
                 Q=self.Q,
                 user_ids=np.array(list(self.user_map.keys()), dtype=np.int64),
                 item_ids=np.array(list(self.item_map.keys()), dtype=np.int64))

    def _try_load_model(self):
        """尝试从磁盘加载模型，返回 True 表示已加载"""
        if np is None:
            return False
        if not os.path.exists(MODEL_FILE):
            return False
        try:
            npz = np.load(MODEL_FILE, allow_pickle=True)
            self.P = npz['P']
            self.Q = npz['Q']
            user_ids = list(map(int, npz['user_ids'].tolist()))
            item_ids = list(map(int, npz['item_ids'].tolist()))
            # rebuild maps
            self.user_map = {uid: idx for idx, uid in enumerate(user_ids)}
            self.item_map = {iid: idx for idx, iid in enumerate(item_ids)}
            self._trained = True
            return True
        except Exception:
            return False

    def recommend(self, user_id: int, top_n=10):
        if not self._trained or user_id not in self.user_map:
            films = Film.query.order_by(db.desc(Film.like_count)).limit(top_n).all()
            return [(f, f.like_count/100.0) for f in films]

        uidx = self.user_map[user_id]
        scores = {}
        user_vec = self.P[uidx]
        for fid, idx in self.item_map.items():
            pred = user_vec.dot(self.Q[idx])
            scores[fid] = pred
        # remove already interacted
        interacted = {it.film_id for it in UserFilmInteraction.query.filter_by(user_id=user_id).all()}
        candidates = [(fid, sc) for fid,sc in scores.items() if fid not in interacted]
        candidates.sort(key=lambda x: x[1], reverse=True)
        result = []
        for fid, sc in candidates[:top_n]:
            film = Film.query.get(fid)
            if film:
                result.append((film, float(sc)))
        return result


# 全局实例
item_recommender = ItemBasedRecommender()
mf_recommender = MatrixFactorizationRecommender()


