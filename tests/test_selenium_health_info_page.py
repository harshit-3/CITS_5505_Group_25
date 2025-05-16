import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timezone, timedelta
import time
import socket
from threading import Thread
from app import create_app, db
from config import TestConfig
from app.models import User, ExerciseEntry, DietEntry, SleepEntry, Message, ShareToken
from werkzeug.security import generate_password_hash

class SeleniumTestBase(unittest.TestCase):
    """Base class for Selenium tests with common setup and teardown."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Find an available port
        self.port = self._find_available_port()
        self.base_url = f"http://localhost:{self.port}"

        # Start Flask app in a separate thread
        self.server_thread = Thread(target=self.app.run, kwargs={'host': 'localhost', 'port': self.port})
        self.server_thread.daemon = True  # Ensure thread terminates when test exits
        self.server_thread.start()

        # Wait for the Flask app to start (up to 5 seconds)
        self._wait_for_server()

        # Set up Selenium WebDriver (Chrome)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)  # Implicit wait for elements

        # Create test users
        self.user1 = User(email="user1@example.com", password=generate_password_hash("password123"))
        self.user2 = User(email="user2@example.com", password=generate_password_hash("password123"))
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        """Tear down the test environment after each test."""
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _find_available_port(self):
        """Find an available port starting from 5000."""
        port = 5000
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return port
                except OSError:
                    port += 1

    def _wait_for_server(self):
        """Wait for the Flask server to be available."""
        timeout = 5  # seconds
        start_time = time.time()
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(('localhost', self.port))
                    return
            except (ConnectionRefusedError, socket.timeout):
                if time.time() - start_time > timeout:
                    raise Exception("Flask server did not start within timeout period")
                time.sleep(0.5)
class TestSeleniumHealthInfoPage(SeleniumTestBase):
    def test_health_info_page(self):
        """Test viewing health info via a share link (pagination removed)."""
        # Insert test data for user1
        for i in range(15):
            exercise = ExerciseEntry(
                user_id=self.user1.id,
                duration=30 + i,
                calories=200 + i * 10,
                date=datetime(2025, 5, 15, tzinfo=timezone.utc).date(),
                workout_type="Running"
            )
            diet = DietEntry(
                user_id=self.user1.id,
                calories=500 + i * 10,
                date=datetime(2025, 5, 15, tzinfo=timezone.utc).date(),
                meal_type="Breakfast",
                food_name="Oatmeal"
            )
            sleep = SleepEntry(
                user_id=self.user1.id,
                sleep_start=datetime(2025, 5, 15, 23, 0, tzinfo=timezone.utc),
                sleep_end=datetime(2025, 5, 16, 7, 0, tzinfo=timezone.utc),
                efficiency=0.85,
                sleep_type="Deep"
            )
            db.session.add_all([exercise, diet, sleep])
        db.session.commit()

        # Create a share token
        share_token = ShareToken(
            token="testtoken123",
            user_id=self.user1.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.session.add(share_token)
        db.session.commit()

        # Log in as user1
        driver = self.driver
        driver.get(f"{self.base_url}/login")
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for redirect to dashboard and verify login success
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        success_message = driver.find_element(By.CLASS_NAME, "alert-success").text
        self.assertIn("Login successful!", success_message)

        # Access health info page
        driver.get(f"{self.base_url}/health_info/testtoken123")

        # Verify all 15 exercise entries are displayed
        exercise_rows = driver.find_elements(By.XPATH, "//h3[text()='Recent Exercise Entries']/following-sibling::table[1]//tbody/tr")
        self.assertEqual(len(exercise_rows), 15)

if __name__ == '__main__':
    unittest.main()