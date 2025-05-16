# test_share_page.py
# This file contains unit tests for the /share page, covering access control,
# fitness data display in charts, message sharing, share link generation,
# QR code rendering, social media sharing links, and UI elements like flash messages
# and chart download functionality.

import unittest
import re
from datetime import datetime, timedelta, timezone
from app import create_app, db
from config import TestConfig
from app.models import User, ExerciseEntry, DietEntry, SleepEntry, Message, ShareToken
from werkzeug.security import generate_password_hash

class SharePageUnitTests(unittest.TestCase):
    """Unit tests for the /share page, testing access, data display, sharing, and UI elements."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create test users
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

    def test_share_page_requires_login(self):
        """Test that unauthenticated users are redirected to login from /share."""
        response = self.client.get("/share", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_share_page_loads_for_logged_in_user(self):
        """Test that /share page loads successfully for a logged-in user."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Share Your Progress", response.data)

    def test_share_page_displays_fitness_data_in_charts(self):
        """Test that /share page passes fitness data to Chart.js for rendering."""
        # Add sample fitness data
        today = datetime.today().date()
        exercise = ExerciseEntry(
            user_id=self.user1.id, duration=30, calories=200, heart_rate=100,
            date=today, workout_type="Running"
        )
        diet = DietEntry(
            user_id=self.user1.id, calories=500, water=1000, protein=30,
            carbs=50, fats=10, date=today, meal_type="Breakfast", food_name="Oatmeal"
        )
        sleep = SleepEntry(
            user_id=self.user1.id, sleep_start=datetime(2025, 5, 15, 23, 0),
            sleep_end=datetime(2025, 5, 16, 7, 0), wake_ups=2, efficiency=0.85,
            sleep_type="Deep"
        )
        db.session.add_all([exercise, diet, sleep])
        db.session.commit()

        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)

        # Verify chart data in JavaScript (chartData object)
        self.assertIn(b'exercise_durations: [30]', response.data)  # Exercise duration
        self.assertIn(b'diet_calories: [500]', response.data)  # Diet calories
        self.assertIn(b'sleep_duration: [8.0]', response.data)  # Sleep duration

    def test_share_page_renders_charts(self):
        """Test that /share page renders all Chart.js canvases for fitness data."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)

        # Verify all chart canvases are present
        chart_ids = [
            b"DailyExerciseDurationChart", b"ExerciseIntensityLevelsChart",
            b"CaloriesBurnedperSessionChart", b"WeeklyExerciseFrequencyChart",
            b"DailyCaloricIntakeChart", b"MacronutrientBreakdownChart",
            b"WaterConsumptionChart", b"WeeklyMealFrequencyChart",
            b"DailySleepDurationChart", b"SleepQualityScoresChart",
            b"SleepTypeDistributionChart", b"SleepWakeupsChart"
        ]
        for chart_id in chart_ids:
            self.assertIn(chart_id, response.data)

    def test_share_page_renders_sharing_form(self):
        """Test that /share page renders the email sharing form correctly."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)

        # Verify form elements
        self.assertIn(b'<form method="POST" action="/share">', response.data)
        self.assertIn(b'<input type="email" class="form-control" id="receiver_email" name="receiver_email" required>', response.data)
        self.assertIn(b'<button type="submit" class="btn btn-primary">Share via Email</button>', response.data)

    def test_share_page_renders_share_link(self):
        """Test that /share page renders the share link and copy button."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)

        # Verify share link input and copy button
        self.assertIn(b'<input type="text" id="share-link" class="form-control"', response.data)
        self.assertIn(b'<button class="btn btn-outline-secondary" type="button" id="copy-link-btn"', response.data)

        # Extract share_url from response and verify format
        share_url_match = re.search(rb'value="(http://[^"]+/health_info/[^"]+)"', response.data)
        self.assertIsNotNone(share_url_match)
        share_url = share_url_match.group(1).decode('utf-8')
        # Allow share_url without port number (e.g., http://127.0.0.1/health_info/<token>)
        self.assertTrue(re.match(r"http://[^/]+(:[0-9]+)?/health_info/[\w]+", share_url))

    def test_share_page_renders_qr_code(self):
        """Test that /share page renders the QR code for the share link."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)

        # Verify QR code image and download button
        self.assertIn(b'<div id="qrcode" class="mx-auto">', response.data)
        self.assertIn(b'<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=', response.data)
        self.assertIn(b'<button class="btn btn-outline-primary mt-3" onclick="downloadQRCode()">', response.data)

    def test_share_page_renders_social_media_links(self):
        """Test that /share page renders social media sharing links with correct URLs."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)

        # Verify social media links
        social_links = {
            b"https://twitter.com/intent/tweet": b"Share on X",
            b"https://discord.com/channels/@me": b"Share on Discord",
            b"https://www.tiktok.com/upload": b"Share on TikTok",
            b"https://www.instagram.com": b"Share on Instagram",
            b"https://www.youtube.com": b"Share on YouTube",
            b"https://www.linkedin.com/feed/?shareActive=true": b"Share on LinkedIn"
        }
        for url, title in social_links.items():
            self.assertIn(url, response.data)
            self.assertIn(title, response.data)

    def test_share_page_renders_download_charts_button(self):
        """Test that /share page renders the button to download all charts."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)

        # Verify download button
        self.assertIn(b'<button class="btn btn-primary download-all-btn" onclick="downloadAllCharts()">', response.data)

    def test_share_message_success(self):
        """Test successfully sharing a message via /share."""
        self.login_user(self.user1.id)
        response = self.client.post("/share", data={
            "receiver_email": "user2@example.com"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Health information shared successfully!", response.data)

        # Verify message in database
        message = Message.query.filter_by(sender_id=self.user1.id, receiver_id=self.user2.id).first()
        self.assertIsNotNone(message)
        # Match the actual summary based on /share route
        self.assertTrue(message.content.startswith("Sharing the recording! View my health information: "))
        self.assertFalse(message.is_read)

        # Verify ShareToken creation
        share_token = ShareToken.query.filter_by(user_id=self.user1.id).first()
        self.assertIsNotNone(share_token)
        self.assertTrue(message.content.endswith(f"/health_info/{share_token.token}"))


    def test_share_prevents_sending_to_self(self):
        """Test that /share prevents a user from sending a message to themselves."""
        self.login_user(self.user1.id)
        response = self.client.post("/share", data={
            "receiver_email": "user1@example.com"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You cannot share with yourself.", response.data)

    def test_share_with_invalid_recipient(self):
        """Test that /share fails when the recipient email is invalid."""
        self.login_user(self.user1.id)
        response = self.client.post("/share", data={
            "receiver_email": "nonexistent@example.com"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User with this email not found.", response.data)

if __name__ == '__main__':
    unittest.main()