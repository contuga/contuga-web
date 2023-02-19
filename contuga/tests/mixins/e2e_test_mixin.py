from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

UserModel = get_user_model()


class EndToEndTestMixin:
    def login(self):
        self.navigate_to_login_form()
        self.fill_login_form(self.user_email, self.user_password)
        self.submit_login_form()

    def navigate_to_login_form(self):
        current_url = self.selenium.current_url

        link = self.selenium.find_element(By.LINK_TEXT, "Login")
        link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def fill_login_form(self, email, password):
        # The username is an email
        email_input = self.selenium.find_element(By.NAME, "username")
        email_input.send_keys(email)

        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys(password)

    def submit_login_form(self):
        current_url = self.selenium.current_url

        button = self.selenium.find_element(
            By.XPATH, '//button[contains(text(), "Login")]'
        )
        button.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def go_back(self):
        current_url = self.selenium.current_url
        self.selenium.back()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )
