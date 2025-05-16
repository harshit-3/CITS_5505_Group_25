from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from test_base import SeleniumTestBase

class TestSeleniumShareAndSendMessage(SeleniumTestBase):
    def test_share_and_send_message(self):
        """Test sharing health info and sending a message."""
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

        # Navigate to share page
        driver.get(f"{self.base_url}/share")

        # Wait for receiver_email field to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "receiver_email"))
        )

        # Fill in share form
        driver.find_element(By.ID, "receiver_email").send_keys("user2@example.com")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        success_message = driver.find_element(By.CLASS_NAME, "alert-success").text
        self.assertIn("Health information shared successfully!", success_message)

if __name__ == '__main__':
    unittest.main()