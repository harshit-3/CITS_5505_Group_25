import sys
import os
import subprocess
import signal
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from config import TestConfig

class AnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run.py'))
        cls.server = subprocess.Popen(
            [sys.executable, run_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        time.sleep(2)

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("http://localhost:5000/login")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        self.driver.find_element(By.NAME, "email").send_keys("495843466@qq.com")
        self.driver.find_element(By.NAME, "password").send_keys("123456789")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @classmethod
    def tearDownClass(cls):
        os.killpg(os.getpgid(cls.server.pid), signal.SIGTERM)

    def test_upload_and_analyze_data(self):
        # After successful login, go to the dashboard page
        self.driver.get("http://localhost:5000/dashboard")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-title")))

        # Verify that key dashboard content is present in the page
        page_source = self.driver.page_source
        self.assertIn("Welcome to Your Dashboard", page_source)
        self.assertIn("Track your fitness journey with ease", page_source)

        # Click the link to the analysis page
        self.driver.find_element(By.PARTIAL_LINK_TEXT, "Analysis").click()
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Fitness Data Analysis')]"))
        )

        # Verify that the analysis page data container exists
        self.assertIn("Fitness Data Analysis", self.driver.page_source)

        # Click to return to the dashboard
        self.driver.back()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-title")))

if __name__ == "__main__":
    unittest.main()