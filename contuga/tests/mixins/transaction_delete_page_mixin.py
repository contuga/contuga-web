from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class TransactionDeletePageMixin:
    def verify_transaction_delete_page(self, transaction, should_navigate=True):
        if should_navigate:
            self.navigate_to_transaction_delete_page(transaction)

        self.verify_delete_page_confirmation_question(transaction)
        self.verify_delete_page_amount(transaction)
        self.verify_delete_page_type(transaction)
        self.verify_delete_page_account(transaction)
        self.verify_delete_page_currency(transaction)
        self.verify_delete_page_category(transaction)
        self.verify_delete_page_tags(transaction)
        self.verify_delete_page_created_at(transaction)
        self.verify_delete_page_updated_at(transaction)

    def navigate_to_transaction_delete_page(self, transaction):
        current_url = self.selenium.current_url

        table = self.selenium.find_element_by_id("transactions")
        tbody = table.find_element_by_tag_name("tbody")
        update_url = reverse("transactions:delete", kwargs={"pk": transaction.pk})

        link = tbody.find_element_by_xpath(f"//a[@href='{update_url}']")
        link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def verify_delete_page_amount(self, transaction):
        self.verify_detail_page_amount(transaction)

    def verify_delete_page_type(self, transaction):
        self.verify_detail_page_type(transaction)

    def verify_delete_page_account(self, transaction):
        self.verify_detail_page_account(transaction)

    def verify_delete_page_currency(self, transaction):
        self.verify_detail_page_currency(transaction)

    def verify_delete_page_category(self, transaction):
        self.verify_detail_page_category(transaction)

    def verify_delete_page_tags(self, transaction):
        self.verify_detail_page_tags(transaction)

    def verify_delete_page_created_at(self, transaction):
        self.verify_detail_page_created_at(transaction)

    def verify_delete_page_updated_at(self, transaction):
        self.verify_detail_page_updated_at(transaction)

    def verify_delete_page_confirmation_question(self, transaction):
        element = self.selenium.find_element_by_tag_name("p")
        text = element.text
        expected_text = _("Are you sure you want to delete this transaction?")

        self.assertEqual(text, expected_text)
