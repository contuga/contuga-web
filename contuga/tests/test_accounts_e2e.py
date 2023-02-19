from decimal import Decimal

from django.contrib.staticfiles.testing import LiveServerTestCase
from django.utils import formats
from django.utils.translation import ugettext as _
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from contuga.contrib.transactions import constants as transaction_constants
from contuga.mixins import TestMixin
from contuga.tests.mixins.e2e_test_mixin import EndToEndTestMixin


# StaticLiveServerTestCase doesn't work as expected
# See https://github.com/jazzband/django-pipeline/issues/593
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
        self.user = self.create_user(email=self.user_email, password=self.user_password)

        self.currency = self.create_currency()
        self.account = self.create_account()
        self.category = self.create_category()

        second_currency = self.create_currency(name="Euro", code="EUR")
        second_account = self.create_account(
            name="Second account", currency=second_currency
        )
        second_category = self.create_category(name="Second category")

        self.create_transaction(amount=Decimal(0.53))
        self.create_transaction(amount=Decimal(73), category=second_category)
        self.create_transaction(amount=Decimal(20.34), account=second_account)

        self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal(900.40)
        )
        self.create_transaction(
            type=transaction_constants.INCOME,
            amount=Decimal(1300),
            category=second_category,
        )
        self.create_transaction(
            type=transaction_constants.INCOME,
            amount=Decimal(2500),
            account=second_account,
        )

    def test_accounts(self):
        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_accounts_list()

        accounts = self.user.accounts.order_by("name")

        self.verify_account_list(accounts)
        self.verify_account_detail_pages(accounts)

    def navigate_to_accounts_list(self):
        current_url = self.selenium.current_url

        link = self.selenium.find_element(By.LINK_TEXT, "View all accounts")

        # Clicking the link used to work with the plain HTML version.
        # Now, when the styles are loaded, the link is not visible on load.
        # Using the firefox driver, the link could not be scrolled into view
        # and cannot be manually scrolled due to MoveTargetOutOfBoundsException
        # The RETURN key appears to be workking fine so far.
        link.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def verify_account_list(self, accounts):
        table = self.selenium.find_element(By.ID, "accounts")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        for index, account in enumerate(accounts):
            with self.subTest(row_index=index):
                row = rows[index]
                columns = row.find_elements(By.TAG_NAME, "td")

                self.verify_name(columns, account)
                self.verify_currency(columns, account)
                self.verify_balance(columns, account)
                self.verify_status(columns, account)

    def verify_name(self, columns, account):
        name = columns[0].text
        expected_name = account.name

        self.assertEqual(name, expected_name)

    def verify_currency(self, columns, account):
        currency = columns[1].text
        expected_currency = account.currency.name

        self.assertEqual(currency, expected_currency)

    def verify_balance(self, columns, account):
        element = columns[2]
        self.verify_balance_value(element, account)
        self.verify_balance_classes(element, account)

    def verify_balance_value(self, element, account):
        balance = element.text
        expected_balance = formats.localize(account.balance, use_l10n=True)

        self.assertEqual(balance, expected_balance)

    def verify_balance_classes(self, element, account):
        classes = element.get_attribute("class").strip()
        expected_classes = "text-success" if account.balance >= 0 else "text-danger"

        self.assertEqual(classes, expected_classes)

    def verify_status(self, columns, account):
        status = columns[3].text
        expected_status = _("Active") if account.is_active else _("Archived")

        self.assertEqual(status, expected_status)

    def verify_account_detail_pages(self, accounts):
        for index, account in enumerate(accounts):
            with self.subTest(row_index=index):
                self.navigate_to_account_detail_page(account)

                self.verify_detail_page_h1(account)
                self.verify_detail_page_name(account)
                self.verify_detail_page_currency(account)
                self.verify_detail_page_balance(account)
                self.verify_detail_page_description(account)
                self.verify_detail_page_created_at(account)
                self.verify_detail_page_updated_at(account)
                self.verify_detail_page_status(account)

                self.go_back()

    def navigate_to_account_detail_page(self, account):
        current_url = self.selenium.current_url

        table = self.selenium.find_element(By.ID, "accounts")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        link = tbody.find_element(
            By.XPATH, f"//a[@href='{account.get_absolute_url()}']"
        )
        link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def verify_detail_page_h1(self, account):
        h1_element = self.selenium.find_element(By.TAG_NAME, "h1")
        text = h1_element.text
        expected_text = _("Account details")

        self.assertEqual(text, expected_text)

    def verify_detail_page_name(self, account):
        expected_label = _("Name")
        expected_value = account.name

        self.verify_detail_page_row(0, expected_label, expected_value)

    def verify_detail_page_currency(self, account):
        expected_label = _("Currency")
        expected_value = account.currency.name

        self.verify_detail_page_row(1, expected_label, expected_value)

    def verify_detail_page_balance(self, account):
        expected_label = _("Balance")
        expected_value = formats.localize(account.balance, use_l10n=True)

        self.verify_detail_page_row(2, expected_label, expected_value)

    def verify_detail_page_description(self, account):
        expected_label = _("Description")
        expected_value = account.description

        self.verify_detail_page_row(3, expected_label, expected_value)

    def verify_detail_page_created_at(self, account):
        expected_label = _("Created at")
        expected_value = formats.date_format(
            account.created_at.astimezone(), "SHORT_DATETIME_FORMAT"
        )

        self.verify_detail_page_row(4, expected_label, expected_value)

    def verify_detail_page_updated_at(self, account):
        expected_label = _("Updated at")
        expected_value = formats.date_format(
            account.updated_at.astimezone(), "SHORT_DATETIME_FORMAT"
        )

        self.verify_detail_page_row(5, expected_label, expected_value)

    def verify_detail_page_status(self, account):
        expected_label = _("Status")
        expected_value = _("Active") if account.is_active else _("Archived")

        self.verify_detail_page_row(6, expected_label, expected_value)

    def verify_detail_page_row(self, index, expected_label, expected_value):
        table = self.selenium.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        row = rows[index]

        label = row.find_element(By.TAG_NAME, "th").text
        self.assertEqual(label, expected_label)

        value = row.find_element(By.TAG_NAME, "td").text
        self.assertEqual(value, expected_value)
