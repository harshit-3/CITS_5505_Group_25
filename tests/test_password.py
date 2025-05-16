# test_password.py
# This file contains unit tests for password handling, including hashing and validation
# during user registration and login.

import unittest
import re
from datetime import datetime, timezone
from app import create_app, db
from config import TestConfig
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

class PasswordUnitTests(unittest.TestCase):
    """Unit tests for password hashing and validation during registration and login."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Tear down the test environment after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashed_on_registration(self):
        """Test that passwords are hashed and salted during registration."""
        response = self.client.post("/register", data={
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "password": "testpassword123",
            "birthdate": "1990-01-01",
            "gender": "Male",
            "country": "USA"
        }, follow_redirects=True)

        # Verify the user in the database
        user = User.query.filter_by(email="testuser@example.com").first()
        self.assertIsNotNone(user, "User should be created in the database")

        # Check that the password is not stored as plain text
        self.assertNotEqual(user.password, "testpassword123", "Password should not be stored as plain text")
        # Check that the password is hashed (match scrypt or pbkdf2 format: method:params$salt$hash or method$salt$hash)
        self.assertTrue(re.match(r"[\w:]+(?:\$\w+){2}", user.password), "Password should be in hashed format (method[:params]$salt$hash)")
        # Verify the hash with the original password
        self.assertTrue(check_password_hash(user.password, "testpassword123"), "Password hash should match the original password")

        # Check for flash message in the response (rendered by base.html)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<div class="alert alert-success', response.data)
        self.assertIn(b"Registration successful! Please log in.", response.data)

    def test_password_validation_on_login(self):
        """Test that login validates the password correctly using hash."""
        # Register a user with a hashed password
        response = self.client.post("/register", data={
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "password": "testpassword123",
            "birthdate": "1990-01-01",
            "gender": "Male",
            "country": "USA"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Test login with correct password
        response = self.client.post("/login", data={
            "email": "testuser@example.com",
            "password": "testpassword123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<div class="alert alert-success', response.data)
        self.assertIn(b"Login successful!", response.data)

        # Test login with incorrect password
        response = self.client.post("/login", data={
            "email": "testuser@example.com",
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Incorrect password.", response.data)

if __name__ == '__main__':
    unittest.main()