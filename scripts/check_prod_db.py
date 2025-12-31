#!/usr/bin/env python3
import os
import sys

from app import create_app
from models.film import Film

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    app = create_app("production")
    with app.app_context():
        print("FILM COUNT:", Film.query.count())


if __name__ == "__main__":
    main()
