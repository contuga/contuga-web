from decimal import Decimal

from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from contuga.contrib.categories import constants as category_constants
from contuga.contrib.categories.models import Category
from contuga.contrib.tags.models import Tag
from contuga.contrib.transactions import constants as transaction_constants
from contuga.contrib.transactions.models import Transaction
from contuga.mixins import TestMixin
from contuga.tests.mixins.e2e_test_mixin import EndToEndTestMixin
from contuga.tests.mixins.transaction_delete_page_mixin import \
    TransactionDeletePageMixin
from contuga.tests.mixins.transaction_detail_page_mixin import \
    TransactionDetailPageMixin
from contuga.tests.mixins.transaction_form_page_mixin import \
    TransactionFormPageMixin
from contuga.tests.mixins.transaction_list_page_mixin import \
    TransactionListPageMixin


# StaticLiveServerTestCase doesn't work as expected
# See https://github.com/jazzband/django-pipeline/issues/593
class SeleniumTestCase(
    LiveServerTestCase,
    TestMixin,
    EndToEndTestMixin,
    TransactionFormPageMixin,
    TransactionListPageMixin,
    TransactionDetailPageMixin,
    TransactionDeletePageMixin,
):
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
        self.second_account = self.create_account(
            name="Second account", currency=second_currency
        )
        self.second_category = self.create_category(name="Second category")

        self.create_transaction(amount=Decimal(0.53))
        self.create_transaction(amount=Decimal(73), category=self.second_category)
        self.create_transaction(amount=Decimal(20.34), account=self.second_account)

        self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal(900.40)
        )
        self.create_transaction(
            type=transaction_constants.INCOME,
            amount=Decimal(1300),
            category=self.second_category,
        )
        self.create_transaction(
            type=transaction_constants.INCOME,
            amount=Decimal(2500),
            account=self.second_account,
        )

    def test_transaction_list_and_detail(self):
        self.selenium.get(self.live_server_url)
        self.login()

        transactions = self.user.transactions.order_by("-created_at")

        self.verify_transaction_list(transactions)
        self.verify_transaction_detail_pages(transactions)

    def test_transaction_create(self):
        self.selenium.get(self.live_server_url)
        self.login()

        old_transaction_count = Transaction.objects.count()

        self.navigate_to_transaction_create_page()
        self.fill_transaction_form(
            type="Income",
            amount="3.14",
            account_name=self.account.name,
            category_name=self.category.name,
            tags=["First tag", "Second tag"],
            description="Transaction description",
        )
        self.submit_transaction_form()

        new_transaction_count = Transaction.objects.count()

        self.assertEqual(new_transaction_count, old_transaction_count + 1)

        transaction = Transaction.objects.order_by("created_at").last()

        self.assertEqual(transaction.type, transaction_constants.INCOME)
        self.assertEqual(transaction.amount, Decimal("3.14"))
        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.category, self.category)
        self.assertEqual(transaction.description, "Transaction description")

        self.verify_transaction_detail_page(transaction, should_navigate=False)

    def test_transaction_create_category_type_change(self):
        income_category = self.create_category(
            name="Income category", transaction_type=category_constants.INCOME
        )
        expenditure_category = self.create_category(
            name="Expenditure category", transaction_type=category_constants.EXPENDITURE
        )

        empty_label = "---------"  # TODO: Move out

        expected_income_category_options = [
            (str(category.pk), category.name)
            for category in Category.objects.exclude(
                transaction_type=category_constants.EXPENDITURE
            ).filter(author=self.user)
        ]
        expected_income_category_options.insert(0, ("", empty_label))

        expected_expenditure_category_options = [
            (str(category.pk), category.name)
            for category in Category.objects.exclude(
                transaction_type=category_constants.INCOME
            ).filter(author=self.user)
        ]
        expected_expenditure_category_options.insert(0, ("", empty_label))

        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_transaction_create_page()

        form = self.selenium.find_element_by_xpath("//main/div/div/form")
        type_input = Select(form.find_element_by_name("type"))
        category_input = Select(form.find_element_by_name("category"))

        # Verify that the transaction type is EXPENDITURE by default
        self.verify_transaction_type_input(
            input=type_input, type=transaction_constants.EXPENDITURE
        )

        # Verify that no category is selected
        self.verify_no_category_is_selected(input=category_input)

        # Verify that only categories with transction_type EXPENDITURE or ALL are available as options
        self.verify_category_options(
            input=category_input, expected_options=expected_expenditure_category_options
        )

        # Select the expenditure category
        category_input.select_by_visible_text(expenditure_category.name)

        # Verify that the expenditure category is selected
        self.verify_category_input(input=category_input, category=expenditure_category)

        # Change the transaction type to INCOME
        type_input.select_by_visible_text("Income")

        # Verify that no category is selected
        self.verify_no_category_is_selected(input=category_input)

        # Verify that only categories with transction_type INCOME or ALL are available as options
        self.verify_category_options(
            input=category_input, expected_options=expected_income_category_options
        )

        # Select the income category
        category_input.select_by_visible_text(income_category.name)

        # Verify that the income category is selected
        self.verify_category_input(input=category_input, category=income_category)

        # Change the transaction type to EXPENDITURE
        type_input.select_by_visible_text("Expenditure")

        # Verify that no category is selected
        self.verify_no_category_is_selected(input=category_input)

        # Verify that only categories with transction_type EXPENDITURE or ALL are available as options
        self.verify_category_options(
            input=category_input, expected_options=expected_expenditure_category_options
        )

    def test_transaction_update(self):
        transaction = self.create_transaction(
            type=transaction_constants.EXPENDITURE,
            amount=Decimal("41.30"),
            account=self.account,
            category=self.category,
            description="Transaction description",
        )

        old_transaction_count = Transaction.objects.count()
        old_tags_count = Tag.objects.count()

        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_transaction_update_page(transaction)
        self.fill_transaction_form(
            type="Income",
            amount="3.14",
            account_name=self.second_account.name,
            category_name=self.second_category.name,
            tags=["First new tag", "Second new tag"],
            description="Updated transaction description",
            should_clear_inputs=True,
            should_clear_tags=True,
        )

        self.submit_transaction_form()

        new_transaction_count = Transaction.objects.count()
        new_tags_count = Tag.objects.count()

        self.assertEqual(new_transaction_count, old_transaction_count)
        self.assertEqual(new_tags_count, old_tags_count + 2)

        updated_transaction = Transaction.objects.get(pk=transaction.pk)

        self.assertEqual(updated_transaction.type, transaction_constants.INCOME)
        self.assertEqual(updated_transaction.amount, Decimal("3.14"))
        self.assertEqual(updated_transaction.account, self.second_account)
        self.assertEqual(updated_transaction.category, self.second_category)
        self.assertEqual(transaction.tags.count(), 2)
        self.assertEqual(transaction.tags.first().name, "First new tag")
        self.assertEqual(transaction.tags.last().name, "Second new tag")
        self.assertEqual(
            updated_transaction.description, "Updated transaction description"
        )

        self.verify_transaction_detail_page(updated_transaction, should_navigate=False)

    def test_transaction_update_without_clearing_tags(self):
        initial_tag = self.create_tag(name="Initial tag")
        transaction = self.create_transaction(
            type=transaction_constants.EXPENDITURE,
            amount=Decimal("41.30"),
            account=self.account,
            category=self.category,
            tags=[initial_tag],
            description="Transaction description",
        )

        old_transaction_count = Transaction.objects.count()
        old_tags_count = Tag.objects.count()

        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_transaction_update_page(transaction)
        self.fill_transaction_form(
            type="Income",
            amount="3.14",
            account_name=self.second_account.name,
            category_name=self.second_category.name,
            tags=["First new tag", "Second new tag"],
            description="Updated transaction description",
            should_clear_inputs=True,
            should_clear_tags=False,
        )

        self.submit_transaction_form()

        new_transaction_count = Transaction.objects.count()
        new_tags_count = Tag.objects.count()

        self.assertEqual(new_transaction_count, old_transaction_count)
        self.assertEqual(new_tags_count, old_tags_count + 2)

        updated_transaction = Transaction.objects.get(pk=transaction.pk)

        self.assertEqual(updated_transaction.type, transaction_constants.INCOME)
        self.assertEqual(updated_transaction.amount, Decimal("3.14"))
        self.assertEqual(updated_transaction.account, self.second_account)
        self.assertEqual(updated_transaction.category, self.second_category)
        self.assertEqual(transaction.tags.count(), 3)

        tags = transaction.tags.order_by("created_at").all()

        self.assertEqual(tags[0].name, "Initial tag")
        self.assertEqual(tags[1].name, "First new tag")
        self.assertEqual(tags[2].name, "Second new tag")
        self.assertEqual(
            updated_transaction.description, "Updated transaction description"
        )

        self.verify_transaction_detail_page(updated_transaction, should_navigate=False)

    def test_transaction_update_income_category(self):
        category = self.create_category(
            name="Income category", transaction_type=category_constants.INCOME
        )

        transaction = self.create_transaction(
            type=transaction_constants.INCOME,
            amount=Decimal("41.30"),
            account=self.account,
            category=category,
            description="Transaction description",
        )

        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_transaction_update_page(transaction)
        form = self.selenium.find_element_by_xpath("//main/div/div/form")

        category_input = Select(form.find_element_by_name("category"))

        self.verify_category_input(input=category_input, category=category)

    def test_transaction_update_expenditure_category(self):
        category = self.create_category(
            name="Income category", transaction_type=category_constants.EXPENDITURE
        )

        transaction = self.create_transaction(
            type=transaction_constants.EXPENDITURE,
            amount=Decimal("41.30"),
            account=self.account,
            category=category,
            description="Transaction description",
        )

        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_transaction_update_page(transaction)
        form = self.selenium.find_element_by_xpath("//main/div/div/form")

        category_input = Select(form.find_element_by_name("category"))

        self.verify_category_input(input=category_input, category=category)

    def test_transaction_update_category_type_change(self):
        income_category = self.create_category(
            name="Income category", transaction_type=category_constants.INCOME
        )
        expenditure_category = self.create_category(
            name="Expenditure category", transaction_type=category_constants.EXPENDITURE
        )

        empty_label = "---------"

        expected_income_category_options = [
            (str(category.pk), category.name)
            for category in Category.objects.exclude(
                transaction_type=category_constants.EXPENDITURE
            ).filter(author=self.user)
        ]
        expected_income_category_options.insert(0, ("", empty_label))

        expected_expenditure_category_options = [
            (str(category.pk), category.name)
            for category in Category.objects.exclude(
                transaction_type=category_constants.INCOME
            ).filter(author=self.user)
        ]
        expected_expenditure_category_options.insert(0, ("", empty_label))

        transaction = self.create_transaction(
            type=transaction_constants.INCOME,
            amount=Decimal("41.30"),
            account=self.account,
            category=income_category,
            description="Transaction description",
        )

        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_transaction_update_page(transaction)

        form = self.selenium.find_element_by_xpath("//main/div/div/form")
        type_input = Select(form.find_element_by_name("type"))
        category_input = Select(form.find_element_by_name("category"))

        # Verify that the income category is selected
        self.verify_category_input(input=category_input, category=income_category)

        # Verify that only categories with transction_type INCOME or ALL are available as options
        self.verify_category_options(
            input=category_input, expected_options=expected_income_category_options
        )

        # Change the transaction type to EXPENDITURE
        type_input.select_by_visible_text("Expenditure")

        # Verify that no category is selected
        self.verify_no_category_is_selected(input=category_input)

        # Verify that only categories with transction_type EXPENDITURE or ALL are available as options
        self.verify_category_options(
            input=category_input, expected_options=expected_expenditure_category_options
        )

        # Select the expenditure category
        category_input.select_by_visible_text(expenditure_category.name)

        # Verify that the expenditure category is selected
        self.verify_category_input(input=category_input, category=expenditure_category)

        # Change the transaction type to INCOME
        type_input.select_by_visible_text("Income")

        # Verify that no category is selected
        self.verify_no_category_is_selected(input=category_input)

        # Verify that only categories with transction_type INCOME or ALL are available as options
        self.verify_category_options(
            input=category_input, expected_options=expected_income_category_options
        )

    def test_transaction_delete(self):
        transaction = self.create_transaction(
            type=transaction_constants.EXPENDITURE,
            amount=Decimal("41.30"),
            account=self.account,
            category=self.category,
            description="Transaction description",
        )

        old_transaction_count = Transaction.objects.count()

        self.selenium.get(self.live_server_url)
        self.login()

        self.navigate_to_transaction_delete_page(transaction)
        self.verify_transaction_delete_page(transaction, should_navigate=False)
        self.submit_transaction_form(button_text="Confirm")

        new_transaction_count = Transaction.objects.count()

        self.assertEqual(new_transaction_count, old_transaction_count - 1)

        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(pk=transaction.pk)
