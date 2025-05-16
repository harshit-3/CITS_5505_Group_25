from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from test_base import SeleniumTestBase

class TestSeleniumLogin(SeleniumTestBase):
    def test_login(self):
        """Test user login functionality."""
        driver = self.driver
        driver.get(f"{self.base_url}/login")

        # Wait for email field to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "email"))
        )

        # Fill in login form
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for redirect and check for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        success_message = driver.find_element(By.CLASS_NAME, "alert-success").text
        self.assertIn("Login successful!", success_message)

if __name__ == '__main__':
    unittest.main()