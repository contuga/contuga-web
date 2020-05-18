from contuga.contrib.accounts.constants import BGN
from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.models import Category
from contuga.contrib.transactions.constants import EXPENDITURE
from contuga.contrib.transactions.models import Transaction


class OnlyAuthoredByCurrentUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


class OnlyOwnedByCurrentUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class TestMixin:
    def create_category(
        self,
        name="Category name",
        author=None,
        transaction_type=EXPENDITURE,
        description="Category description",
    ):
        return Category.objects.create(
            name=name,
            author=author or self.user,
            transaction_type=transaction_type,
            description=description,
        )

    def create_account(
        self, name="Account name", currency=BGN, owner=None, is_active=True
    ):
        return Account.objects.create(
            name=name, currency=currency, owner=owner or self.user, is_active=is_active
        )

    def create_transaction(
        self,
        amount=100,
        type=EXPENDITURE,
        author=None,
        category=None,
        account=None,
        description="Transaction description",
    ):
        return Transaction.objects.create(
            amount=amount,
            type=type,
            author=author or self.user,
            category=category or self.category or None,
            account=account or self.account,
            description=description,
        )
