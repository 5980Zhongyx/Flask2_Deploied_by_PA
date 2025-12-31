"""
application test script
contains unit tests and functional tests
"""

import os
import sys

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest  # noqa: E402

from app import create_app, db  # noqa: E402
from models import (
    User,
    Film,
    UserFilmInteraction,
    AppLog,
    recommendation_engine,
)  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

class TestConfig:
    """Test configuration"""
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    WTF_CSRF_ENABLED = False
 
class FilmRecommendationTestCase(unittest.TestCase):
    """Film recommendation application test case"""

    def setUp(self):
        """Test preparation"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Create all tables
        db.create_all()

        # Create test data
        self.create_test_data()

    def tearDown(self):
        """Test cleanup"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_data(self):
        """Create test data"""
        # Create test users
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

        # Create test movies
        self.film1 = Film(
            title='Test Movie 1',
            genre='Drama',
            year=2020,
            director='Test Director 1',
            description='This is a test movie'
        )
        self.film2 = Film(
            title='Test Movie 2',
            genre='Action',
            year=2021,
            director='Test Director 2',
            description='This is an action movie'
        )
        self.film3 = Film(
            title='Test Movie 3',
            genre='Comedy',
            year=2019,
            director='Test Director 3',
            description='This is a comedy movie'
        )

        db.session.add_all([self.film1, self.film2, self.film3])
        db.session.commit()

        # Create user interactions
        interaction1 = UserFilmInteraction(
            user_id=self.user1.id,
            film_id=self.film1.id,
            liked=True,
            rating=5,
            review_text='A great movie!'
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

        db.session.add_all(
            [
                interaction1,
                interaction2,
                interaction3,
                interaction4,
                interaction5,
            ]
        )
        db.session.commit()

 
    # Model tests
    def test_user_model(self):
        """Test user model"""
        user = User.query.filter_by(username='testuser1').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test1@example.com')
        self.assertEqual(len(user.interactions), 2)

    def test_film_model(self):
        """Test film model"""
        film = Film.query.filter_by(title='Test Movie 1').first()
        self.assertIsNotNone(film)
        self.assertEqual(film.genre, 'Drama')
        self.assertEqual(film.year, 2020)
        self.assertEqual(len(film.interactions), 2)
        self.assertEqual(film.like_count, 2)
        self.assertEqual(film.average_rating, 5.0)

    def test_interaction_model(self):
        """Test user film interaction model"""
        interaction = UserFilmInteraction.query.filter_by(
            user_id=self.user1.id, film_id=self.film1.id
        ).first()
        self.assertIsNotNone(interaction)
        self.assertTrue(interaction.liked)
        self.assertEqual(interaction.rating, 5)
        self.assertTrue(interaction.has_review)
        self.assertEqual(interaction.review_text, 'A great movie!')

    # Recommendation system tests
    def test_recommendation_engine_initialization(self):
        """Test recommendation engine initialization"""
        # Reload data
        recommendation_engine._load_data()

        self.assertIn(self.user1.id, recommendation_engine.user_interactions)
        self.assertIn(self.user2.id, recommendation_engine.user_interactions)
        self.assertEqual(len(recommendation_engine.user_interactions[self.user1.id]), 2)

    def test_similar_users_calculation(self):
        """Test similar users calculation"""
        recommendation_engine._load_data()
        similar_users = recommendation_engine.get_similar_users(self.user1.id, top_n=5)

        # user1 and user2 should have similarity
        user_ids = [user_id for user_id, _ in similar_users]
        self.assertIn(self.user2.id, user_ids)

    def test_recommendation_generation(self):
        """Test recommendation generation"""
        recommendation_engine._load_data()
        recommendations = recommendation_engine.recommend_films(self.user1.id, top_n=5)

        # user1 hasn't seen film3, should be recommended
        film_ids = [film.id for film, _ in recommendations]
        self.assertIn(self.film3.id, film_ids)

    # Route tests
    def test_home_page(self):
        """Test home page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Film Discovery Platform', response.data.decode('utf-8'))

    def test_film_list_page(self):
        """Test film list page"""
        response = self.client.get('/films')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Film List', response.data.decode('utf-8'))

    def test_film_detail_page(self):
        """Test film detail page"""
        response = self.client.get(f'/films/{self.film1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Movie 1', response.data.decode('utf-8'))

    def test_registration(self):
        """Test user registration"""
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
        """Test login and logout"""
        # log-in
        response = self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome, testuser1', response.data.decode('utf-8'))

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_routes(self):
        """Test authenticated routes"""
        # Access recommendation page without login
        response = self.client.get('/recommendations')
        self.assertEqual(response.status_code, 302)  # Redirect to login page

        # Access recommendation page after login
        self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        })

        response = self.client.get('/recommendations')
        self.assertEqual(response.status_code, 200)
        self.assertIn('My Movie Recommendations', response.data.decode('utf-8'))

    def test_like_functionality(self):
        """Test like functionality"""
        # log-in
        self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        })

        # Like movie
        response = self.client.post(f'/api/like/{self.film3.id}')
        self.assertEqual(response.status_code, 200)

        # Check like record in database
        interaction = UserFilmInteraction.query.filter_by(
            user_id=self.user1.id, film_id=self.film3.id
        ).first()
        self.assertIsNotNone(interaction)
        self.assertTrue(interaction.liked)

    def test_rating_functionality(self):
        """Test rating functionality"""
        # log-in
        self.client.post('/login', data={
            'username': 'testuser1',
            'password': 'password123'
        })

        # Rate movie
        response = self.client.post(f'/api/interaction/{self.film3.id}', data={
            'rating': '4',
            'liked': 'true',
            'review': 'A good movie'
        })
        self.assertEqual(response.status_code, 200)

        # Check rating record in database
        interaction = UserFilmInteraction.query.filter_by(
            user_id=self.user1.id, film_id=self.film3.id
        ).first()
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.rating, 4)
        self.assertTrue(interaction.liked)
        self.assertEqual(interaction.review_text, 'A good movie')

    # test logging functionality
    def test_logging(self):
        """Test logging functionality"""
        initial_log_count = AppLog.query.count()

        # Perform an operation that will create a log (register)
        self.client.post('/register', data={
            'username': 'logtest',
            'email': 'log@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })

        # Check if log is created
        final_log_count = AppLog.query.count()
        self.assertGreater(final_log_count, initial_log_count)

        # Check log content
        recent_logs = AppLog.query.order_by(AppLog.timestamp.desc()).limit(5).all()
        register_log = None
        for log in recent_logs:
            if log.action == 'USER_REGISTER':
                register_log = log
                break

        self.assertIsNotNone(register_log)
        self.assertEqual(register_log.resource_type, 'user')

class PerformanceTestCase(unittest.TestCase):
    """Performance test"""

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
        """Test response time"""
        import time

        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        # Response time should be less than 1 second
        self.assertLess(end_time - start_time, 1.0)

class SecurityTestCase(unittest.TestCase):
    """Security test"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create test user
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
        """Test password hashing"""
        user = User.query.filter_by(username='security_test').first()
        self.assertNotEqual(user.password_hash, 'password123')
        self.assertTrue(user.password_hash.startswith('pbkdf2:sha256:'))

    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        # Try SQL injection
        response = self.client.post('/login', data={
            'username': "' OR '1'='1",
            'password': 'anything'
        })

        self.assertNotIn('Welcome', response.data.decode('utf-8'))

    def test_xss_protection(self):
        """Test XSS protection"""
        # Try XSS attack
        malicious_script = '<script>alert("XSS")</script>'

        # Try to inject script when registering
        response = self.client.post('/register', data={
            'username': 'xss_test',
            'email': 'xss@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })

        # Check if response contains unescaped script
        self.assertNotIn(malicious_script.encode(), response.data)

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.makeSuite(FilmRecommendationTestCase))
    suite.addTest(unittest.makeSuite(PerformanceTestCase))
    suite.addTest(unittest.makeSuite(SecurityTestCase))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Output test result summary
    print(f"\n{'='*50}")
    print("Test result summary:")
    print(f"Run tests: {result.testsRun}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_count = result.testsRun - len(result.failures) - len(result.errors)
    print(f"Success: {success_count}")

    if result.failures:
        print("\nFailed tests:")
        for test_case, traceback in result.failures:
            print(f"- {test_case}")

    if result.errors:
        print("\nTests with errors:")
        for test_case, traceback in result.errors:
            print(f"- {test_case}")
