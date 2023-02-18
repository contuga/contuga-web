from django.contrib.auth import get_user_model

from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.constants import ALL
from contuga.contrib.categories.models import Category
from contuga.contrib.currencies.models import Currency
from contuga.contrib.settings.models import Settings
from contuga.contrib.tags.models import Tag
from contuga.contrib.transactions.constants import EXPENDITURE, INCOME
from contuga.contrib.transactions.models import Transaction

UserModel = get_user_model()


class OnlyAuthoredByCurrentUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


class OnlyOwnedByCurrentUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class SettingsMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.settings = self.get_settings()

    def get_settings(self):
        if not self.request.user.is_authenticated:
            return None

        return (
            Settings.objects.filter(user=self.request.user)
            .select_related(
                "default_expenditures_category",
                "default_incomes_category",
                "default_account",
            )
            .first()
        )


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

    def create_tag(self, name="Tag", author=None, transactions=None):
        return Tag.objects.create(name=name, author=author or self.user)

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
        tags=None,
        account=None,
        description=None,
    ):
        try:
            category = category or self.category
        except AttributeError:
            pass

        try:
            tags = tags or self.tags
        except AttributeError:
            tags = []

        transaction = Transaction.objects.create(
            amount=amount or 100,
            type=type,
            author=author or self.user or account.user
            if account
            else self.account.owner,
            category=category,
            account=account or self.account,
            description=description or "Transaction description",
        )

        for tag in tags:
            transaction.tags.add(tag)

        return transaction

    def create_income(
        self,
        amount=None,
        author=None,
        category=None,
        tags=None,
        account=None,
        description=None,
    ):
        return self.create_transaction(
            type=INCOME,
            amount=amount,
            author=author,
            category=category,
            tags=tags,
            account=account,
            description=description,
        )

    def create_expenditure(
        self,
        amount=None,
        author=None,
        category=None,
        tags=None,
        account=None,
        description=None,
    ):
        return self.create_transaction(
            type=EXPENDITURE,
            amount=amount,
            author=author,
            category=category,
            tags=tags,
            account=account,
            description=description,
        )
