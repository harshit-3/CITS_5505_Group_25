from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from test_base import SeleniumTestBase

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