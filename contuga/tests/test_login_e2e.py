from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

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

    def setUp(self):
        self.user_email = "john.doe@example.com"
        self.user_password = "password"
        self.user = self.create_user(email=self.user_email, password=self.user_password)

    def test_login(self):
        self.selenium.get(self.live_server_url)

        self.login()
        self.verify_login_is_complete()

    def verify_login_is_complete(self):
        link = self.selenium.find_element_by_link_text(self.user.email)

        self.assertTrue(link.is_displayed())
