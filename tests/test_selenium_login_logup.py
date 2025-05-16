import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from config import TestConfig
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import subprocess
import time
import uuid
import os
import signal

class AuthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run.py'))
        cls.server = subprocess.Popen(
            [sys.executable, run_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Start a process group to allow easy termination
        )
        time.sleep(2)  # Wait for Flask server to start
        if cls.server.poll() is not None:
            stderr_output = cls.server.stderr.read().decode()
            raise RuntimeError(f"Flask failed to start:\n{stderr_output}")
        cls.app = create_app(TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    def setUp(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        self.test_email = f"test_{uuid.uuid4()}@example.com"

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        os.killpg(os.getpgid(cls.server.pid), signal.SIGTERM)  # Terminate Flask server

    def tearDown(self):
        self.driver.quit()

    def test_register_and_login(self):
        self.driver.get("http://localhost:5000/register")
        self.driver.find_element(By.NAME, "first_name").send_keys("Test")
        self.driver.find_element(By.NAME, "last_name").send_keys("User")
        self.driver.find_element(By.NAME, "email").send_keys(self.test_email)
        self.driver.find_element(By.NAME, "password").send_keys("test1234")
        birthdate_input = self.driver.find_element(By.NAME, "birthdate")
        birthdate_input.clear()
        birthdate_input.send_keys("2000-01-01")
        Select(self.driver.find_element(By.NAME, "gender")).select_by_visible_text("Other")
        Select(self.driver.find_element(By.NAME, "country")).select_by_visible_text("Australia")
        self.driver.find_element(By.ID, "subscribe").click()
        self.driver.execute_script("document.querySelector('form').submit()")
        time.sleep(2)

        self.assertIn("Log In", self.driver.page_source)

        self.driver.get("http://localhost:5000/login")
        self.driver.find_element(By.ID, "email").send_keys(self.test_email)
        self.driver.find_element(By.ID, "password").send_keys("test1234")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        self.assertIn("Dashboard", self.driver.page_source)


if __name__ == '__main__':
    unittest.main()