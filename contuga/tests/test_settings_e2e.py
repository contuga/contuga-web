from django.contrib.staticfiles.testing import LiveServerTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from contuga.contrib.categories.constants import EXPENDITURE, INCOME
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
        self.default_income_category = self.create_category(
            name="Salary",
            transaction_type=INCOME,
        )
        self.default_expenditure_category = self.create_category(
            name="Food",
            transaction_type=EXPENDITURE,
        )
        self.default_account = self.create_account(
            name="Cash account",
            currency=self.currency,
        )

        self.user.settings.default_incomes_category = self.default_income_category
        self.user.settings.default_expenditures_category = self.default_expenditure_category
        self.user.settings.default_account = self.default_account
        self.user.settings.save()

    def test_settings_detail_page(self):
        self.selenium.get(self.live_server_url)
        self.login()

        self.selenium.get(f"{self.live_server_url}{reverse('settings:detail')}")

        self.assertEqual(self.selenium.find_element(By.TAG_NAME, "h1").text, "Settings")

        body = self.selenium.find_element(By.TAG_NAME, "body").text
        self.assertIn(self.default_income_category.name, body)
        self.assertIn(self.default_expenditure_category.name, body)
        self.assertIn(self.default_account.name, body)

    def test_settings_change(self):
        self.selenium.get(self.live_server_url)
        self.login()

        income_category = self.create_category(name="Bonus", transaction_type=INCOME)
        expenditure_category = self.create_category(
            name="Bills",
            transaction_type=EXPENDITURE,
        )
        account = self.create_account(name="Savings account", currency=self.currency)

        self.selenium.get(f"{self.live_server_url}{reverse('settings:update')}")

        Select(self.selenium.find_element(By.NAME, "default_incomes_category")).select_by_visible_text(
            income_category.name
        )
        Select(self.selenium.find_element(By.NAME, "default_expenditures_category")).select_by_visible_text(
            expenditure_category.name
        )
        Select(self.selenium.find_element(By.NAME, "default_account")).select_by_visible_text(
            account.name
        )
        self.selenium.find_element(By.NAME, "transactions_per_page").clear()
        self.selenium.find_element(By.NAME, "transactions_per_page").send_keys("25")

        self.selenium.find_element(By.XPATH, '//button[contains(text(), "Save")]').click()

        self.selenium.get(f"{self.live_server_url}{reverse('settings:detail')}")

        body = self.selenium.find_element(By.TAG_NAME, "body").text
        self.assertIn(income_category.name, body)
        self.assertIn(expenditure_category.name, body)
        self.assertIn(account.name, body)
        self.assertIn("25", body)
