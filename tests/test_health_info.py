# test_health_info.py
# This file contains unit tests for the Health Info sharing feature, focusing on
# the /health_info/<token> route and its access control.

import unittest
from datetime import datetime
from app import create_app, db
from config import TestConfig
from app.models import User
from werkzeug.security import generate_password_hash

class HealthInfoUnitTests(unittest.TestCase):
    """Unit tests for Health Info sharing feature, covering access to /health_info/<token>."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.user1 = User(email="user1@example.com", password=generate_password_hash("pass1"))
        self.user2 = User(email="user2@example.com", password=generate_password_hash("pass2"))
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        """Tear down the test environment after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_user(self, user_id):
        """Helper method to log in a user by setting user_id in session."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id

    def test_health_info_page_public_access(self):
        """Test that unauthenticated users are redirected to login when accessing /health_info/<token>."""
        with self.client.session_transaction() as sess:
            sess["share_tokens"] = [{"token": "testtoken", "user_id": self.user1.id}]

        response = self.client.get("/health_info/testtoken")
        self.assertEqual(response.status_code, 302)  # Expect redirect to login
        self.assertIn("/login", response.headers["Location"])

    def test_health_info_page_invalid_token(self):
        """Test that accessing /health_info/<token> with an invalid token redirects to login."""
        response = self.client.get("/health_info/invalidtoken")
        self.assertEqual(response.status_code, 302)  # Expect redirect to login
        self.assertIn("/login", response.headers["Location"])

if __name__ == '__main__':
    unittest.main()