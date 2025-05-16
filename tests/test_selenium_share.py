import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys
import subprocess
import signal
from app import create_app, db
from config import TestConfig
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class ShareFeatureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run.py'))
        # Start Flask app in a subprocess
        cls.server = subprocess.Popen(
            [sys.executable, run_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        time.sleep(2)  # Give server time to start

        cls.app = create_app(TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Configure automatic download without confirmation
        download_dir = os.path.abspath("downloads")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.default_directory": download_dir,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get("http://localhost:5000/login")

    def tearDown(self):
        self.driver.quit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        os.killpg(os.getpgid(cls.server.pid), signal.SIGTERM)

    def test_share_feature_flow(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # Log in
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys("495843466@qq.com")
        password_input.send_keys("123456789")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Go to the share page
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Dashboard")))
        driver.get("http://localhost:5000/share")

        # Wait for QR code to appear
        wait.until(EC.presence_of_element_located((By.ID, "qrcode")))

        # Copy the share link
        copy_btn = driver.find_element(By.ID, "copy-link-btn")
        copy_btn.click()

        # Download QR code
        qr_download_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Download QR Code')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", qr_download_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", qr_download_btn)
        time.sleep(2)

        # Download all charts
        download_all_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Download All Charts')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", download_all_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", download_all_btn)
        time.sleep(3)

        # Return to the dashboard
        dashboard_link = driver.find_element(By.LINK_TEXT, "Dashboard")
        driver.execute_script("arguments[0].scrollIntoView(true);", dashboard_link)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", dashboard_link)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-title")))

        # Simple assertion to ensure the flow completes
        self.assertIn("Dashboard", driver.page_source)

if __name__ == "__main__":
    unittest.main()