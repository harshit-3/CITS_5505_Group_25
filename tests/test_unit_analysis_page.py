import unittest
from datetime import datetime
from app import create_app, db
from config import TestConfig
from app.models import User, ExerciseEntry
from werkzeug.security import generate_password_hash

class AnalysisPageUnitTests(unittest.TestCase):
    def setUp(self):
        # Create the test app
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        # Push application context to use Flask features like sessions and db
        self.app_context.push()

        # Initialize the database
        db.create_all()

        # Flask test client
        self.client = self.app.test_client()

        # Create a test user
        self.test_user = User(email="test@example.com", password=generate_password_hash("testpass"))
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        # Clear the database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Helper method to log in test user
    def login_test_user(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.test_user.id

    def test_requires_login_redirects(self):
        response = self.client.get("/analysis", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_analysis_page_loads_for_logged_in_user(self):
        self.login_test_user()
        response = self.client.get("/analysis")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Fitness Data Analysis", response.data)


    # This test inserts multiple entries for exercise, diet, and sleep across two days.
    # It then verifies that aggregated values are correctly passed to the frontend
    # and appear in the HTML response as expected JavaScript data.
    def test_full_analysis_with_multiple_entries(self):
        self.login_test_user()

        # --- Exercise data: two different days ---
        from app.models import ExerciseEntry, DietEntry, SleepEntry  # Import additional models for test data
        db.session.add_all([
            ExerciseEntry(user_id=self.test_user.id, duration=30, calories=200, heart_rate=100, date=datetime(2025, 5, 1)),
            ExerciseEntry(user_id=self.test_user.id, duration=45, calories=300, heart_rate=110, date=datetime(2025, 5, 2))
        ])

        # --- Diet data: two different days ---
        db.session.add_all([
            DietEntry(user_id=self.test_user.id, calories=500, water=1000, protein=30, carbs=50, fats=10, date=datetime(2025, 5, 1)),
            DietEntry(user_id=self.test_user.id, calories=700, water=1500, protein=40, carbs=60, fats=15, date=datetime(2025, 5, 2))
        ])

        # --- Sleep data: two different days ---
        db.session.add_all([
            SleepEntry(user_id=self.test_user.id, sleep_start=datetime(2025, 5, 1, 23, 0), sleep_end=datetime(2025, 5, 2, 7, 0),
                       wake_ups=2, efficiency=0.85, sleep_type="Deep"),
            SleepEntry(user_id=self.test_user.id, sleep_start=datetime(2025, 5, 2, 23, 0), sleep_end=datetime(2025, 5, 3, 6, 0),
                       wake_ups=1, efficiency=0.9, sleep_type="Light")
        ])

        db.session.commit()

        # --- Request page ---
        response = self.client.get("/analysis")
        self.assertEqual(response.status_code, 200)

        # --- Exercise checks ---
        self.assertIn(b"[30, 45]", response.data)  # Verify durations list in JS context
        self.assertIn(b"[200, 300]", response.data)  # exercise_calories
        self.assertIn(b"[500, 700]", response.data)  # diet_calories
        self.assertIn(b"[1000, 1500]", response.data)  # diet_water
        self.assertIn(b"[8.0, 7.0]", response.data)  # sleep_duration
        self.assertIn(b"[0.85, 0.9]", response.data)  # sleep_efficiency
        self.assertIn(b"[100.0, 110.0]", response.data)
        self.assertIn(b"[30.0, 40.0]", response.data)  # protein
        self.assertIn(b"[50.0, 60.0]", response.data)  # carbs
        self.assertIn(b"[10.0, 15.0]", response.data)  # fats
        self.assertIn(b"[2, 1]", response.data)  # wake_ups
        self.assertIn(b"['Deep', 'Light']", response.data)  # sleep_type