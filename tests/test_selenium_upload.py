import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import subprocess
import signal
import unittest
from app import create_app, db
from config import TestConfig
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager


class UploadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Launch the Flask application server in a subprocess
        # Start Flask test server
        run_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run.py'))
        cls.server = subprocess.Popen(
            [sys.executable, run_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        time.sleep(2)  # 等待服务器启动

    @classmethod
    def tearDownClass(cls):
        # Stop Flask test server
        os.killpg(os.getpgid(cls.server.pid), signal.SIGTERM)
    def setUp(self):
        # Set up in-memory database environment
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Initialize headless Chrome WebDriver for Selenium testing
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(10)
        self.driver.get("http://localhost:5000/login")

        # Log in
        self.driver.find_element(By.NAME, "email").send_keys("495843466@qq.com")
        self.driver.find_element(By.NAME, "password").send_keys("123456789")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        self.driver.get("http://localhost:5000/upload")

    def test_upload_exercise(self):
        # Test the exercise upload form with sample input
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "exercise")))
        try:
            self.driver.find_element(By.ID, "exercise-tab").click()
        except Exception as e:
            print(f"Could not click exercise-tab: {e}")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "exercise")))
        Select(self.driver.find_element(By.NAME, "workout_type")).select_by_visible_text("Running")
        Select(self.driver.find_element(By.NAME, "intensity")).select_by_visible_text("Medium")
        self.driver.find_element(By.NAME, "duration").send_keys("30")
        self.driver.find_element(By.NAME, "distance").send_keys("5")
        self.driver.find_element(By.NAME, "calories").send_keys("300")
        self.driver.find_element(By.NAME, "heart_rate").send_keys("120")
        self.driver.find_element(By.NAME, "date").send_keys("2025-05-16")
        self.driver.find_element(By.NAME, "notes").send_keys("Selenium test exercise")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "#exercise button[type='submit']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#exercise button[type='submit']"))).click()
        time.sleep(1)

    def test_upload_diet(self):
        # Test the diet upload form with sample input
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "diet")))
        try:
            self.driver.find_element(By.ID, "diet-tab").click()
        except Exception as e:
            print(f"Could not click diet-tab: {e}")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "diet")))
        Select(self.driver.find_element(By.NAME, "meal_type")).select_by_visible_text("Lunch")
        self.driver.find_element(By.NAME, "food_name").send_keys("Chicken Salad")
        self.driver.find_element(By.NAME, "diet_calories").send_keys("450")
        self.driver.find_element(By.NAME, "meal_time").send_keys("12:30")
        self.driver.find_element(By.NAME, "protein").send_keys("25")
        self.driver.find_element(By.NAME, "carbs").send_keys("30")
        self.driver.find_element(By.NAME, "fats").send_keys("15")
        self.driver.find_element(By.NAME, "water").send_keys("250")
        self.driver.find_element(By.NAME, "diet_date").send_keys("2025-05-16")
        self.driver.find_element(By.NAME, "diet_notes").send_keys("Selenium test diet")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "#diet button[type='submit']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#diet button[type='submit']"))).click()
        time.sleep(1)

    def test_upload_sleep(self):
        # Test the sleep upload form with sample input
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "sleep")))
        try:
            self.driver.find_element(By.ID, "sleep-tab").click()
        except Exception as e:
            print(f"Could not click sleep-tab: {e}")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "sleep")))
        self.driver.find_element(By.NAME, "sleep_start").send_keys("2025-05-15T23:00")
        self.driver.find_element(By.NAME, "sleep_end").send_keys("2025-05-16T07:00")
        Select(self.driver.find_element(By.NAME, "sleep_quality")).select_by_visible_text("Good")
        self.driver.find_element(By.NAME, "wake_ups").send_keys("1")
        self.driver.find_element(By.NAME, "efficiency").send_keys("90")
        Select(self.driver.find_element(By.NAME, "sleep_type")).select_by_visible_text("Night")
        self.driver.find_element(By.NAME, "sleep_notes").send_keys("Selenium test sleep")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "#sleep button[type='submit']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#sleep button[type='submit']"))).click()
        time.sleep(1)

    def tearDown(self):
        # Clean up Selenium WebDriver and test database context
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

if __name__ == "__main__":
    unittest.main()