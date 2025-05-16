import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from config import TestConfig
import signal
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import subprocess
import time
import socket


class DashboardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Flask app in a subprocess
        run_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run.py'))
        cls.server = subprocess.Popen(
            [sys.executable, run_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Allows us to later terminate the whole process group
        )
        time.sleep(2)  # Wait briefly for server to boot

        # Prepare the test app context and database
        cls.app = create_app(TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @staticmethod
    def wait_for_server(host, port, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection((host, port), timeout=1):
                    return True
            except OSError:
                time.sleep(0.5)
        raise RuntimeError("Flask server did not start in time")

    def setUp(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)

        # Visit login page first
        self.driver.get("http://localhost:5000/login")

        # Simulate login form input
        email_input = self.driver.find_element(By.ID, "email")
        password_input = self.driver.find_element(By.ID, "password")
        email_input.send_keys("495843466@qq.com")
        password_input.send_keys("123456789")

        # Submit login form
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # Redirect to dashboard after login
        self.driver.get("http://localhost:5000/dashboard")

    def tearDown(self):
        self.driver.quit()

    @classmethod
    def tearDownClass(cls):
        # Remove DB session and drop all tables
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

        # Stop the Flask server
        os.killpg(os.getpgid(cls.server.pid), signal.SIGTERM)

    def test_dashboard_loads(self):
        self.assertIn("Welcome to Your Dashboard", self.driver.page_source)

    def test_cards_displayed(self):
        expected_cards = [
            "Upload Data",
            "Analyze Data",
            "Exercise Records",
            "Diet Records",
            "Sleep Records",
            "Share Progress"
        ]
        for text in expected_cards:
            with self.subTest(card=text):
                self.assertIn(text, self.driver.page_source)


if __name__ == '__main__':
    unittest.main()