"""
数据模型模块
"""

from .user import User
from .film import Film
from .interaction import UserFilmInteraction
from .log import AppLog
# recommendation_engine will be imported when needed

__all__ = ['User', 'Film', 'UserFilmInteraction', 'AppLog']
