from datetime import datetime
from app import db

class AppLog(db.Model):
    """应用层日志表，用于审计和记录关键操作"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 操作者信息
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(80), nullable=True)  # 冗余字段，便于查询

    # 操作信息
    action = db.Column(db.String(100), nullable=False, index=True)  # 操作类型
    resource_type = db.Column(db.String(50), nullable=False)  # 资源类型 (user, film, interaction等)
    resource_id = db.Column(db.Integer, nullable=True)  # 资源ID

    # 操作详情
    description = db.Column(db.Text, nullable=False)  # 详细描述
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4/IPv6地址
    user_agent = db.Column(db.Text, nullable=True)  # 用户代理字符串

    # 额外数据 (JSON格式存储)
    extra_data = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<AppLog {self.action} by {self.username or "Anonymous"} at {self.timestamp}>'

    @staticmethod
    def log_action(action: str, resource_type: str, description: str,
                  user=None, resource_id=None, ip_address=None,
                  user_agent=None, extra_data=None):
        """记录操作日志的静态方法"""
        from flask import request
        import json

        # 获取请求信息
        if ip_address is None and request:
            ip_address = request.remote_addr
        if user_agent is None and request:
            user_agent = request.headers.get('User-Agent')

        # 创建日志记录
        log_entry = AppLog(
            action=action,
            resource_type=resource_type,
            description=description,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        if user:
            log_entry.user_id = user.id
            log_entry.username = user.username

        if extra_data:
            log_entry.extra_data = json.dumps(extra_data, ensure_ascii=False)

        try:
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            # 日志记录失败不应该影响主业务流程
            print(f"Failed to log action: {e}")
            db.session.rollback()

    @staticmethod
    def get_recent_logs(limit=50):
        """获取最近的日志记录"""
        return AppLog.query.order_by(AppLog.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_user_logs(user_id, limit=20):
        """获取特定用户的日志记录"""
        return AppLog.query.filter_by(user_id=user_id).order_by(AppLog.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_logs_by_action(action, limit=20):
        """获取特定操作类型的日志记录"""
        return AppLog.query.filter_by(action=action).order_by(AppLog.timestamp.desc()).limit(limit).all()
