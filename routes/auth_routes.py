import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models.user import User

auth_bp = Blueprint("auth", __name__)

# 配置日志
auth_logger = logging.getLogger('auth')

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("film.index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # 验证输入
        if not username or not email or not password:
            flash("所有字段都是必填的", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("密码不匹配", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("密码至少需要6个字符", "error")
            return render_template("register.html")

        # 检查用户是否已存在
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("用户名或邮箱已被注册", "error")
            return render_template("register.html")

        # 创建新用户
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # 记录应用层日志
        from models import AppLog
        AppLog.log_action(
            action="USER_REGISTER",
            resource_type="user",
            description=f"用户 {username} 注册成功",
            user=new_user,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        auth_logger.info(f"User registered: {username}")
        flash("注册成功！请登录", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("film.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            # 记录登录成功日志
            from models import AppLog
            AppLog.log_action(
                action="USER_LOGIN_SUCCESS",
                resource_type="user",
                description=f"用户 {username} 登录成功",
                user=user,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )

            auth_logger.info(f"Login successful: {username}")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("film.index"))
        else:
            # 记录登录失败日志
            from models import AppLog
            AppLog.log_action(
                action="USER_LOGIN_FAILED",
                resource_type="user",
                description=f"用户 {username} 登录失败：用户名或密码错误",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                extra_data={"attempted_username": username}
            )

            auth_logger.warning(f"Login failed: {username}")
            flash("用户名或密码错误", "error")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    auth_logger.info(f"Logout: {current_user.username}")
    logout_user()
    flash("已成功登出", "info")
    return redirect(url_for("film.index"))
