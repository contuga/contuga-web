from django.contrib.auth import get_user_model

from contuga.contrib.accounts.constants import BGN
from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.models import Category
from contuga.contrib.categories.constants import ALL
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
    def create_user(self, email="john.doe@example.com", password="password"):
        return UserModel.objects.create_user(email=email, password=password)

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

    def create_account(
        self,
        name="Account name",
        currency=BGN,
        owner=None,
        description="Account description",
        is_active=True,
    ):
        return Account.objects.create(
            name=name,
            currency=currency,
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
            account=account,
            description=description,
        )
