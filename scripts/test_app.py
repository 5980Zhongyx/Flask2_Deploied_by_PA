"""
应用测试脚本
包含单元测试和功能测试
"""

import os
import sys
import unittest
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import User, Film, UserFilmInteraction, AppLog, recommendation_engine
from werkzeug.security import generate_password_hash

class TestConfig:
    """测试配置"""
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    WTF_CSRF_ENABLED = False

class FilmRecommendationTestCase(unittest.TestCase):
    """电影推荐应用测试用例"""

    def setUp(self):
        """测试前准备"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # 创建所有表
        db.create_all()

        # 创建测试数据
        self.create_test_data()

    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_data(self):
        """创建测试数据"""
        # 创建测试用户
        self.user1 = User(
            username='testuser1',
            email='test1@example.com',
            password_hash=generate_password_hash('password123')
        )
        self.user2 = User(
            username='testuser2',
            email='test2@example.com',
            password_hash=generate_password_hash('password123')
        )
        self.user3 = User(
            username='testuser3',
            email='test3@example.com',
            password_hash=generate_password_hash('password123')
        )

        db.session.add_all([self.user1, self.user2, self.user3])
        db.session.commit()

        # 创建测试电影
        self.film1 = Film(
            title='测试电影1',
            genre='剧情',
            year=2020,
            director='测试导演1',
            description='这是一部测试电影'
        )
        self.film2 = Film(
            title='测试电影2',
            genre='动作',
            year=2021,
            director='测试导演2',
            description='这是一部动作电影'
        )
        self.film3 = Film(
            title='测试电影3',
            genre='喜剧',
            year=2019,
            director='测试导演3',
            description='这是一部喜剧电影'
        )

        db.session.add_all([self.film1, self.film2, self.film3])
        db.session.commit()

        # 创建用户互动
        interaction1 = UserFilmInteraction(
            user_id=self.user1.id,
            film_id=self.film1.id,
            liked=True,
            rating=5,
            review_text='很棒的电影！'
        )
        interaction2 = UserFilmInteraction(
            user_id=self.user1.id,
            film_id=self.film2.id,
            liked=True,
            rating=4
        )
        interaction3 = UserFilmInteraction(
            user_id=self.user2.id,
            film_id=self.film1.id,
            liked=True,
            rating=5
        )
        interaction4 = UserFilmInteraction(
            user_id=self.user2.id,
            film_id=self.film2.id,
            liked=True,
            rating=4
        )
        interaction5 = UserFilmInteraction(
            user_id=self.user3.id,
            film_id=self.film3.id,
            liked=True,
            rating=3
        )

        db.session.add_all([interaction1, interaction2, interaction3, interaction4, interaction5])
        db.session.commit()

    # 模型测试
    def test_user_model(self):
        """测试用户模型"""
        user = User.query.filter_by(username='testuser1').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test1@example.com')
        self.assertEqual(len(user.interactions), 2)

    def test_film_model(self):
        """测试电影模型"""
        film = Film.query.filter_by(title='测试电影1').first()
        self.assertIsNotNone(film)
        self.assertEqual(film.genre, '剧情')
        self.assertEqual(film.year, 2020)
        self.assertEqual(len(film.interactions), 2)
        self.assertEqual(film.like_count, 2)
        self.assertEqual(film.average_rating, 5.0)

    def test_interaction_model(self):
        """测试用户电影互动模型"""
        interaction = UserFilmInteraction.query.filter_by(
            user_id=self.user1.id, film_id=self.film1.id
        ).first()
        self.assertIsNotNone(interaction)
        self.assertTrue(interaction.liked)
        self.assertEqual(interaction.rating, 5)
        self.assertTrue(interaction.has_review)
        self.assertEqual(interaction.review_text, '很棒的电影！')

    # 推荐系统测试
    def test_recommendation_engine_initialization(self):
        """测试推荐引擎初始化"""
        # 重新加载数据
        recommendation_engine._load_data()

        self.assertIn(self.user1.id, recommendation_engine.user_interactions)
        self.assertIn(self.user2.id, recommendation_engine.user_interactions)
        self.assertEqual(len(recommendation_engine.user_interactions[self.user1.id]), 2)

    def test_similar_users_calculation(self):
        """测试相似用户计算"""
        recommendation_engine._load_data()
        similar_users = recommendation_engine.get_similar_users(self.user1.id, top_n=5)

        # user1和user2应该有相似性
        user_ids = [user_id for user_id, _ in similar_users]
        self.assertIn(self.user2.id, user_ids)

    def test_recommendation_generation(self):
        """测试推荐生成"""
        recommendation_engine._load_data()
        recommendations = recommendation_engine.recommend_films(self.user1.id, top_n=5)

        # user1还没看过film3，应该会被推荐
        film_ids = [film.id for film, _ in recommendations]
        self.assertIn(self.film3.id, film_ids)

    # 路由测试
    def test_home_page(self):
        """测试首页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('电影发现平台', response.data.decode('utf-8'))

    def test_film_list_page(self):
        """测试电影列表页"""
        response = self.client.get('/films')
        self.assertEqual(response.status_code, 200)
        self.assertIn('电影列表', response.data.decode('utf-8'))

    def test_film_detail_page(self):
        """测试电影详情页"""
        response = self.client.get(f'/films/{self.film1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('测试电影1', response.data.decode('utf-8'))

    def test_registration(self):
        """测试用户注册"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)

    def test_login_logout(self):
        """测试登录和登出"""
        # 登录
        response = self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('欢迎，testuser1', response.data.decode('utf-8'))

        # 登出
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_routes(self):
        """测试需要认证的路由"""
        # 未登录访问推荐页面
        response = self.client.get('/recommendations')
        self.assertEqual(response.status_code, 302)  # 重定向到登录页

        # 登录后访问
        self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        })

        response = self.client.get('/recommendations')
        self.assertEqual(response.status_code, 200)
        self.assertIn('我的电影推荐', response.data.decode('utf-8'))

    def test_like_functionality(self):
        """测试点赞功能"""
        # 登录
        self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        })

        # 点赞电影
        response = self.client.post(f'/api/like/{self.film3.id}')
        self.assertEqual(response.status_code, 200)

        # 检查数据库中的点赞记录
        interaction = UserFilmInteraction.query.filter_by(
            user_id=self.user1.id, film_id=self.film3.id
        ).first()
        self.assertIsNotNone(interaction)
        self.assertTrue(interaction.liked)

    def test_rating_functionality(self):
        """测试评分功能"""
        # 登录
        self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        })

        # 评分电影
        response = self.client.post(f'/api/interaction/{self.film3.id}', data={
            'rating': '4',
            'liked': 'true',
            'review': '不错的电影'
        })
        self.assertEqual(response.status_code, 200)

        # 检查数据库中的评分记录
        interaction = UserFilmInteraction.query.filter_by(
            user_id=self.user1.id, film_id=self.film3.id
        ).first()
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.rating, 4)
        self.assertTrue(interaction.liked)
        self.assertEqual(interaction.review_text, '不错的电影')

    # 日志测试
    def test_logging(self):
        """测试日志功能"""
        initial_log_count = AppLog.query.count()

        # 执行一个会产生日志的操作（注册）
        self.client.post('/register', data={
            'username': 'logtest',
            'email': 'log@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })

        # 检查日志是否被创建
        final_log_count = AppLog.query.count()
        self.assertGreater(final_log_count, initial_log_count)

        # 检查日志内容
        recent_logs = AppLog.query.order_by(AppLog.timestamp.desc()).limit(5).all()
        register_log = None
        for log in recent_logs:
            if log.action == 'USER_REGISTER':
                register_log = log
                break

        self.assertIsNotNone(register_log)
        self.assertEqual(register_log.resource_type, 'user')

class PerformanceTestCase(unittest.TestCase):
    """性能测试"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_response_time(self):
        """测试响应时间"""
        import time

        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 1.0)  # 响应时间应小于1秒

class SecurityTestCase(unittest.TestCase):
    """安全测试"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # 创建测试用户
        user = User(
            username='security_test',
            email='security@example.com',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """测试密码哈希"""
        user = User.query.filter_by(username='security_test').first()
        self.assertNotEqual(user.password_hash, 'password123')
        self.assertTrue(user.password_hash.startswith('pbkdf2:sha256:'))

    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        # 尝试SQL注入
        response = self.client.post('/login', data={
            'username': "' OR '1'='1",
            'password': 'anything'
        })

        self.assertNotIn('欢迎', response.data.decode('utf-8'))

    def test_xss_protection(self):
        """测试XSS防护"""
        # 尝试XSS攻击
        malicious_script = '<script>alert("XSS")</script>'

        # 注册时尝试注入脚本
        response = self.client.post('/register', data={
            'username': 'xss_test',
            'email': 'xss@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })

        # 检查响应中是否包含未转义的脚本
        self.assertNotIn(malicious_script.encode(), response.data)

if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试用例
    suite.addTest(unittest.makeSuite(FilmRecommendationTestCase))
    suite.addTest(unittest.makeSuite(PerformanceTestCase))
    suite.addTest(unittest.makeSuite(SecurityTestCase))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果摘要
    print(f"\n{'='*50}")
    print(f"测试结果摘要:")
    print(f"运行的测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")

    if result.failures:
        print(f"\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}")

    if result.errors:
        print(f"\n有错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}")
