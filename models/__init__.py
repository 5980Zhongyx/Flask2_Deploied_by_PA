"""
数据模型模块
"""

# 避免循环导入，将导入移到需要时进行
def get_models():
    """延迟导入模型以避免循环导入"""
    from .user import User
    from .film import Film
    from .interaction import UserFilmInteraction
    from .log import AppLog
    return User, Film, UserFilmInteraction, AppLog

# 保持向后兼容性
__all__ = ['get_models']
