#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练矩阵分解模型并持久化到 instance/recommendation_mf.npz
用法：python scripts/train_mf.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def main():
    app = create_app('development')
    with app.app_context():
        print("开始训练 Matrix Factorization 模型...")
        # 导入并实例化推荐器，构造时会尝试加载已有模型或训练并保存
        from models.recommendation_advanced import MatrixFactorizationRecommender
        mf = MatrixFactorizationRecommender()
        if getattr(mf, '_trained', False):
            print("训练完成并已持久化模型（instance/recommendation_mf.npz）")
        else:
            print("训练未完成（可能缺少 numpy 或无足够数据）")

if __name__ == '__main__':
    main()


