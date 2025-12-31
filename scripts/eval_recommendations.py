#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估推荐算法（User-based, Item-based, Matrix Factorization）
输出 JSON 报告 scripts/recommendation_eval.json

指标：precision@K (K=5), hit_rate@1 (是否命中单个holdout)
"""
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from models.interaction import UserFilmInteraction

try:
    import numpy as np
except Exception:
    np = None

OUT_FILE = "scripts/recommendation_eval.json"


def build_user_items(interactions):
    u2i = defaultdict(set)
    for it in interactions:
        if it.liked or it.rating or it.has_review:
            u2i[it.user_id].add(it.film_id)
    return u2i


def item_based_recs(train_u2i, user_id, top_n=10):
    # build item->users
    item_users = defaultdict(set)
    for u, items in train_u2i.items():
        for it in items:
            item_users[it].add(u)
    # compute scores
    interacted = train_u2i.get(user_id, set())
    scores = defaultdict(float)
    for item in interacted:
        users_a = item_users.get(item, set())
        for other, users_b in item_users.items():
            if other in interacted:
                continue
            inter = users_a & users_b
            union = users_a | users_b
            sim = (len(inter) / len(union)) if union else 0.0
            scores[other] += sim
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [fid for fid, _ in ranked[:top_n]]


def user_based_recs(train_u2i, user_id, top_n=10):
    # build user vectors (binary)
    users = list(train_u2i.keys())
    items = set()
    for its in train_u2i.values():
        items |= its
    items = list(items)
    item_index = {it: i for i, it in enumerate(items)}
    # build user vectors
    vectors = {}
    for u in users:
        vec = [0] * len(items)
        for it in train_u2i[u]:
            vec[item_index[it]] = 1
        vectors[u] = vec
    if user_id not in vectors:
        return []
    target = vectors[user_id]
    scores = {}
    import math

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    def norm(a):
        return math.sqrt(sum(x * x for x in a))

    for u, vec in vectors.items():
        if u == user_id:
            continue
        denom = norm(vec) * norm(target)
        sim = dot(vec, target) / denom if denom > 0 else 0.0
        # aggregate neighbor's items
        for it in train_u2i[u]:
            if it in train_u2i[user_id]:
                continue
            scores[it] = scores.get(it, 0) + sim
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [fid for fid, _ in ranked[:top_n]]


def mf_recs_train_and_recommend(
    train_interactions, user_id, top_n=10, factors=10, epochs=10, lr=0.01, reg=0.02
):
    if np is None:
        return []
    users = sorted({it.user_id for it in train_interactions})
    items = sorted({it.film_id for it in train_interactions})
    u_map = {u: i for i, u in enumerate(users)}
    i_map = {i: j for j, i in enumerate(items)}
    data = []
    for it in train_interactions:
        score = 0
        if it.liked:
            score += 3
        if it.rating:
            score += it.rating
        if it.has_review:
            score += 1
        if score <= 0:
            continue
        data.append((u_map[it.user_id], i_map[it.film_id], score))
    if user_id not in u_map or not data:
        return []
    num_users = len(users)
    num_items = len(items)
    P = np.random.normal(scale=0.1, size=(num_users, factors))
    Q = np.random.normal(scale=0.1, size=(num_items, factors))
    for epoch in range(epochs):
        for u, i, r in data:
            pred = P[u].dot(Q[i])
            e = r - pred
            P[u] += lr * (e * Q[i] - reg * P[u])
            Q[i] += lr * (e * P[u] - reg * Q[i])
    uidx = u_map[user_id]
    user_vec = P[uidx]
    scores = {}
    for fid, idx in i_map.items():
        scores[fid] = float(user_vec.dot(Q[idx]))
    interacted = {it.film_id for it in train_interactions if it.user_id == user_id}
    candidates = [(fid, sc) for fid, sc in scores.items() if fid not in interacted]
    candidates.sort(key=lambda x: x[1], reverse=True)
    return [fid for fid, _ in candidates[:top_n]]


def evaluate(app, sample_users=200, k=5):
    with app.app_context():
        interactions = UserFilmInteraction.query.order_by(
            UserFilmInteraction.created_at
        ).all()
        u2i_all = build_user_items(interactions)
        users = [u for u, its in u2i_all.items() if len(its) >= 2]
        if not users:
            print("无足够用户用于评估，输出空指标")
            return {
                "n_users": 0,
                "k": k,
                "user_based": {"hit_rate": 0.0, "precision_at_k": 0.0},
                "item_based": {"hit_rate": 0.0, "precision_at_k": 0.0},
                "matrix_factorization": {"hit_rate": 0.0, "precision_at_k": 0.0},
            }
        random.shuffle(users)
        users = users[: min(sample_users, len(users))]
        hits = {"user": 0, "item": 0, "mf": 0}
        precision = {"user": [], "item": [], "mf": []}
        for u in users:
            user_interactions = [it for it in interactions if it.user_id == u]
            if not user_interactions:
                continue
            # holdout last interaction
            test = user_interactions[-1]
            train = [
                it
                for it in interactions
                if not (
                    it.user_id == u
                    and it.film_id == test.film_id
                    and it.created_at == test.created_at
                )
            ]
            train_u2i = build_user_items(train)
            # recommendations
            user_recs = user_based_recs(train_u2i, u, top_n=k)
            item_recs = item_based_recs(train_u2i, u, top_n=k)
            mf_recs = mf_recs_train_and_recommend(train, u, top_n=k, epochs=10)

            # compute hits
            def eval_list(lst):
                hit = 1 if test.film_id in lst else 0
                prec = hit / k
                return hit, prec

            h, p = eval_list(user_recs)
            hits["user"] += h
            precision["user"].append(p)
            h, p = eval_list(item_recs)
            hits["item"] += h
            precision["item"].append(p)
            h, p = eval_list(mf_recs)
            hits["mf"] += h
            precision["mf"].append(p)
        n = len(users)
        results = {
            "n_users": n,
            "k": k,
            "user_based": {
                "hit_rate": hits["user"] / n,
                "precision_at_k": sum(precision["user"]) / n,
            },
            "item_based": {
                "hit_rate": hits["item"] / n,
                "precision_at_k": sum(precision["item"]) / n,
            },
            "matrix_factorization": {
                "hit_rate": hits["mf"] / n,
                "precision_at_k": sum(precision["mf"]) / n,
            },
        }
        return results


if __name__ == "__main__":
    app = create_app("development")
    res = evaluate(app, sample_users=200, k=5)
    os.makedirs("scripts", exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("Evaluation saved to", OUT_FILE)
