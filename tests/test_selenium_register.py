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

class TestSeleniumRegister(SeleniumTestBase):
    def test_register(self):
        """Test user registration functionality."""
        driver = self.driver
        driver.get(f"{self.base_url}/register")

        # Wait for email field to be present (increase timeout to 20 seconds)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
        except Exception as e:
            # Debug: Print page source to inspect HTML
            print("Page source for /register:", driver.page_source)
            raise e

        # Fill in registration form (include all required fields)
        driver.find_element(By.NAME, "first_name").send_keys("Test")
        driver.find_element(By.NAME, "last_name").send_keys("User")
        driver.find_element(By.NAME, "email").send_keys("newuser@example.com")
        driver.find_element(By.NAME, "password").send_keys("newpassword123")

        # Set birthdate using JavaScript to avoid date picker issues
        birthdate_field = driver.find_element(By.NAME, "birthdate")
        driver.execute_script("arguments[0].value = '1990-01-01';", birthdate_field)

        driver.find_element(By.NAME, "gender").send_keys("Male")
        driver.find_element(By.NAME, "country").send_keys("United States")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for redirect to login page (increase timeout to 20 seconds)
        try:
            WebDriverWait(driver, 20).until(
                EC.url_contains("/login")
            )
        except Exception as e:
            # Debug: Print page source to inspect HTML
            print("Page source after registration:", driver.page_source)
            raise e

        # Verify that we are redirected to the login page
        self.assertIn("/login", driver.current_url)

if __name__ == '__main__':
    unittest.main()