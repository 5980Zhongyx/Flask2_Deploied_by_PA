#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
instance/recommendation_mf.npz exercise training matrix factorization model
and persist to instance/recommendation_mf.npz
Usage: python scripts/train_mf.py
"""
import os
import sys

from app import create_app
from models.recommendation_advanced import MatrixFactorizationRecommender

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    app = create_app('development')
    with app.app_context():
        print("Starting to train Matrix Factorization model...")
        mf = MatrixFactorizationRecommender()
        if getattr(mf, '_trained', False):
            print("Training completed and model persisted to "
                  "instance/recommendation_mf.npz")
        else:
            print("Training not completed (possibly missing numpy or "
                  "insufficient data)")


if __name__ == '__main__':
    main()
