from django.utils import formats
from django.utils.translation import ugettext_lazy as _
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class TransactionDetailPageMixin:
    def verify_transaction_detail_page(self, transaction, should_navigate=True):
        if should_navigate:
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

    def verify_transaction_detail_pages(self, transactions):
        for index, transaction in enumerate(transactions):
            with self.subTest(row_index=index):
                self.verify_transaction_detail_page(transaction)
