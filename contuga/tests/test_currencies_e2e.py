from django.contrib.staticfiles.testing import LiveServerTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from contuga.mixins import TestMixin
from contuga.tests.mixins.e2e_test_mixin import EndToEndTestMixin


class SeleniumTestCase(LiveServerTestCase, TestMixin, EndToEndTestMixin):
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
        self.user = self.create_user(
            email=self.user_email,
            password=self.user_password,
        )

        self.currency = self.create_currency(name="United States Dollar", code="USD")
        self.other_currency = self.create_currency(name="Euro", code="EUR")

    def test_currencies_list_and_detail_page(self):
        self.selenium.get(self.live_server_url)
        self.login()

        self.selenium.get(f"{self.live_server_url}{reverse('currencies:list')}")

        body = self.selenium.find_element(By.TAG_NAME, "body").text
        self.assertIn("Currencies", body)
        self.assertIn(self.currency.name, body)
        self.assertIn(self.other_currency.name, body)

        link = self.selenium.find_element(By.LINK_TEXT, self.currency.name)
        link.click()

        self.assertEqual(
            self.selenium.find_element(By.TAG_NAME, "h1").text,
            "Currency details",
        )
        self.assertIn(self.currency.code, self.selenium.page_source)
        self.assertIn(str(self.currency.nominal), self.selenium.page_source)

    def test_currency_create_and_delete(self):
        self.selenium.get(self.live_server_url)
        self.login()

        self.selenium.get(f"{self.live_server_url}{reverse('currencies:create')}")
        self.selenium.find_element(By.NAME, "name").send_keys("British Pound")
        self.selenium.find_element(By.NAME, "code").send_keys("GBP")
        self.selenium.find_element(By.NAME, "nominal").clear()
        self.selenium.find_element(By.NAME, "nominal").send_keys("1")
        self.selenium.find_element(By.XPATH, '//button[contains(text(), "Save")]').click()

        self.assertEqual(
            self.selenium.find_element(By.TAG_NAME, "h1").text,
            "Currency details",
        )
        self.assertIn("British Pound", self.selenium.page_source)

        self.selenium.find_element(By.LINK_TEXT, "Delete").click()
        self.selenium.find_element(By.XPATH, '//button[contains(text(), "Confirm")]').click()

        self.assertNotIn("British Pound", self.selenium.page_source)
