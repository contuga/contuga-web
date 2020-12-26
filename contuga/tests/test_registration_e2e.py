from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import signing
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from contuga.mixins import EndToEndTestMixin, TestMixin


class SeleniumTestCase(StaticLiveServerTestCase, TestMixin, EndToEndTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_registration(self):
        self.selenium.get(self.live_server_url)

        self.navigate_to_registration_form()
        self.fill_registration_form()
        self.submit_registration_form()
        self.verify_registration_complete_page()

        self.navigate_to_activation_page_with_invalid_key()
        self.verify_activation_failed_page()

        self.navigate_to_activation_page()
        self.verify_activation_complete_page()

    def navigate_to_registration_form(self):
        current_url = self.selenium.current_url

        link = self.selenium.find_element_by_link_text("Register")
        link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def fill_registration_form(self):
        email_input = self.selenium.find_element_by_name("email")
        email_input.send_keys("john.doe@example.com")

        password_input = self.selenium.find_element_by_name("password1")
        password_input.send_keys("Secret123+")

        password2_input = self.selenium.find_element_by_name("password2")
        password2_input.send_keys("Secret123+")

    def submit_registration_form(self):
        current_url = self.selenium.current_url

        button = self.selenium.find_element_by_xpath(
            '//button[contains(text(), "Register")]'
        )
        button.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def verify_registration_complete_page(self):
        text = _(
            "Your registration is successful. An activation link has been sent to your email."
        )
        element = self.selenium.find_element_by_xpath(
            f"//*[contains(text(), '{text}')]"
        )

        self.assertTrue(element.is_displayed())

    def navigate_to_activation_page_with_invalid_key(self):
        activation_key = self.get_invalid_activation_key()
        path = reverse("users:activate", args=[activation_key])
        self.selenium.get(f"{self.live_server_url}{path}")

    def get_invalid_activation_key(self):
        return self.get_activation_key(is_valid=False)

    def get_activation_key(self, is_valid=True):
        UserModel = get_user_model()
        user = UserModel.objects.last()
        REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")

        username = user.get_username() if is_valid else "invalid_username"
        return signing.dumps(obj=username, salt=REGISTRATION_SALT)

    def navigate_to_activation_page(self):
        activation_key = self.get_activation_key()
        path = reverse("users:activate", args=[activation_key])
        self.selenium.get(f"{self.live_server_url}{path}")

    def verify_activation_failed_page(self):
        text = _("The account you attempted to activate is invalid.")
        element = self.selenium.find_element_by_xpath(
            f"//*[contains(text(), '{text}')]"
        )

        self.assertTrue(element.is_displayed())

    def verify_activation_complete_page(self):
        text = _("Your activation was successful")
        element = self.selenium.find_element_by_xpath(
            f"//*[contains(text(), '{text}')]"
        )

        self.assertTrue(element.is_displayed())
