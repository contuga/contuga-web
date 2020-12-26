from django.contrib.auth import get_user_model
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.constants import ALL
from contuga.contrib.categories.models import Category
from contuga.contrib.currencies.models import Currency
from contuga.contrib.transactions.constants import EXPENDITURE, INCOME
from contuga.contrib.transactions.models import Transaction

UserModel = get_user_model()


class OnlyAuthoredByCurrentUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


class OnlyOwnedByCurrentUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class TestMixin:
    def create_user(
        self, email="john.doe@example.com", password="password", **extra_fields
    ):
        return UserModel.objects.create_user(
            email=email, password=password, **extra_fields
        )

    def create_category(
        self,
        name="Category name",
        author=None,
        transaction_type=ALL,
        description="Category description",
    ):
        return Category.objects.create(
            name=name,
            author=author or self.user,
            transaction_type=transaction_type,
            description=description,
        )

    def create_currency(self, name="Bulgarian lev", author=None, code="BGN", nominal=1):
        return Currency.objects.create(
            name=name, author=author or self.user, code=code, nominal=nominal
        )

    def create_account(
        self,
        name="Account name",
        currency=None,
        owner=None,
        description="Account description",
        is_active=True,
    ):
        return Account.objects.create(
            name=name,
            currency=currency or self.currency,
            owner=owner or self.user,
            description=description,
            is_active=is_active,
        )

    def create_transaction(
        self,
        amount=None,
        type=EXPENDITURE,
        author=None,
        category=None,
        account=None,
        description=None,
    ):
        try:
            category = category or self.category
        except AttributeError:
            pass

        return Transaction.objects.create(
            amount=amount or 100,
            type=type,
            author=author or self.user or account.user
            if account
            else self.account.owner,
            category=category,
            account=account or self.account,
            description=description or "Transaction description",
        )

    def create_income(
        self, amount=None, author=None, category=None, account=None, description=None
    ):
        return self.create_transaction(
            type=INCOME,
            amount=amount,
            author=author,
            category=category,
            account=account,
            description=description,
        )

    def create_expenditure(
        self, amount=None, author=None, category=None, account=None, description=None
    ):
        return self.create_transaction(
            type=EXPENDITURE,
            amount=amount,
            author=author,
            category=category,
            account=account,
            description=description,
        )


class EndToEndTestMixin:
    def login(self):
        self.navigate_to_login_form()
        self.fill_login_form(self.user_email, self.user_password)
        self.submit_login_form()

    def navigate_to_login_form(self):
        current_url = self.selenium.current_url

        link = self.selenium.find_element_by_link_text("Login")
        link.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )

    def fill_login_form(self, email, password):
        # The username is an email
        email_input = self.selenium.find_element_by_name("username")
        email_input.send_keys(email)

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)

    def submit_login_form(self):
        current_url = self.selenium.current_url

        button = self.selenium.find_element_by_xpath(
            '//button[contains(text(), "Login")]'
        )
        button.click()

        WebDriverWait(self.selenium, 5).until(
            expected_conditions.url_changes(current_url)
        )
