from decimal import Decimal

from django.contrib.staticfiles.testing import LiveServerTestCase
from django.utils import formats
from django.utils.translation import ugettext_lazy as _
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from contuga.contrib.transactions import constants as transaction_constants
from contuga.mixins import EndToEndTestMixin, TestMixin


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
        self.tags = [self.create_tag(), self.create_tag("Second tag")]

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

    def test_transactions(self):
        self.selenium.get(self.live_server_url)
        self.login()

        transactions = self.user.transactions.order_by("-created_at")

        self.verify_transaction_list(transactions)
        self.verify_transaction_detail_pages(transactions)

    def verify_transaction_list(self, transactions):
        table = self.selenium.find_element_by_id("transactions")
        tbody = table.find_element_by_tag_name("tbody")
        rows = tbody.find_elements_by_tag_name("tr")

        for index, transaction in enumerate(transactions):
            with self.subTest(row_index=index):
                row = rows[index]
                columns = row.find_elements_by_tag_name("td")

                self.verify_amount(columns, transaction)
                self.verify_account(columns, transaction)
                self.verify_category(columns, transaction)
                self.verify_created_at(columns, transaction)
                self.verify_description(columns, transaction)

    def verify_amount(self, columns, transaction):
        element = columns[0]
        self.verify_amount_value(element, transaction)
        self.verify_amount_icon_classes(element, transaction)
        self.verify_amount_link_href(element, transaction)
        self.verify_amount_link_classes(element, transaction)

    def verify_amount_value(self, element, transaction):
        amount = element.text
        localized_amount = formats.localize(transaction.amount, use_l10n=True)
        expected_amount = f"{localized_amount} {transaction.currency.representation}"

        self.assertEqual(amount, expected_amount)

    def verify_amount_icon_classes(self, parent, transaction):
        icon = parent.find_element_by_tag_name("i")

        classes = icon.get_attribute("class")
        expected_classes = transaction.type_icon_class

        self.assertEqual(classes, expected_classes)

    def verify_amount_link_href(self, parent, transaction):
        link = parent.find_element_by_tag_name("a")

        href = link.get_attribute("href")
        expected_href = f"{self.live_server_url}{transaction.get_absolute_url()}"

        self.assertEqual(href, expected_href)

    def verify_amount_link_classes(self, parent, transaction):
        link = parent.find_element_by_tag_name("a")

        classes = link.get_attribute("class").strip()
        expected_classes = "text-success" if transaction.is_income else "text-danger"

        self.assertEqual(classes, expected_classes)

    def verify_account(self, columns, transaction):
        account = columns[1].text
        expected_account = transaction.account.name

        self.assertEqual(account, expected_account)

    def verify_category(self, columns, transaction):
        category = columns[2].text
        expected_category = transaction.category.name

        self.assertEqual(category, expected_category)

    def verify_created_at(self, columns, transaction):
        created_at = columns[3].text
        expected_created_at = formats.date_format(
            transaction.created_at.astimezone(), "SHORT_DATETIME_FORMAT"
        )

        self.assertEqual(created_at, expected_created_at)

    def verify_description(self, columns, transaction):
        description = columns[4].text
        expected_description = transaction.description

        self.assertEqual(description, expected_description)

    def verify_transaction_detail_pages(self, transactions):
        for index, transaction in enumerate(transactions):
            with self.subTest(row_index=index):
                self.navigate_to_transaction_detail_page(transaction)
                self.verify_detail_page_h1(transaction)
                self.verify_detail_page_amount(transaction)
                self.verify_detail_page_type(transaction)
                self.verify_detail_page_account(transaction)
                self.verify_detail_page_currency(transaction)
                self.verify_detail_page_category(transaction)
                self.verify_detail_page_tags(transaction)
                self.verify_detail_page_created_at(transaction)
                self.verify_detail_page_updated_at(transaction)
                self.go_back()

    def navigate_to_transaction_detail_page(self, transaction):
        current_url = self.selenium.current_url

        table = self.selenium.find_element_by_id("transactions")
        tbody = table.find_element_by_tag_name("tbody")
        link = tbody.find_element_by_xpath(
            f"//a[@href='{transaction.get_absolute_url()}']"
        )
        link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def verify_detail_page_h1(self, transaction):
        h1_element = self.selenium.find_element_by_tag_name("h1")
        text = h1_element.text
        expected_text = _("Transaction details")

        self.assertEqual(text, expected_text)

    def verify_detail_page_amount(self, transaction):
        expected_label = _("Amount")
        expected_value = formats.localize(transaction.amount, use_l10n=True)
        self.verify_detail_page_row(0, expected_label, expected_value)

    def verify_detail_page_type(self, transaction):
        expected_label = _("Type")
        expected_value = transaction.get_type_display()
        self.verify_detail_page_row(1, expected_label, expected_value)

    def verify_detail_page_account(self, transaction):
        expected_label = _("Account")
        expected_value = transaction.account.name
        self.verify_detail_page_row(2, expected_label, expected_value)

    def verify_detail_page_currency(self, transaction):
        expected_label = _("Currency")
        expected_value = transaction.currency.name
        self.verify_detail_page_row(3, expected_label, expected_value)

    def verify_detail_page_category(self, transaction):
        expected_label = _("Category")
        expected_value = transaction.category.name
        self.verify_detail_page_row(4, expected_label, expected_value)

    def verify_detail_page_tags(self, transaction):
        expected_label = _("Tags")
        expected_value = " ".join(transaction.tags.values_list("name", flat=True))
        self.verify_detail_page_row(5, expected_label, expected_value)

    def verify_detail_page_created_at(self, transaction):
        expected_label = _("Created at")
        expected_value = formats.date_format(
            transaction.created_at.astimezone(), "SHORT_DATETIME_FORMAT"
        )
        self.verify_detail_page_row(6, expected_label, expected_value)

    def verify_detail_page_updated_at(self, transaction):
        expected_label = _("Updated at")
        expected_value = formats.date_format(
            transaction.updated_at.astimezone(), "SHORT_DATETIME_FORMAT"
        )
        self.verify_detail_page_row(7, expected_label, expected_value)

    def verify_detail_page_row(self, index, expected_label, expected_value):
        table = self.selenium.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        row = rows[index]

        label = row.find_element_by_tag_name("th").text
        self.assertEqual(label, expected_label)

        value = row.find_element_by_tag_name("td").text
        self.assertEqual(value, expected_value)
