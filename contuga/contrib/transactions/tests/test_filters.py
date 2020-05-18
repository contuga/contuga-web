from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from contuga.contrib.accounts.constants import BGN
from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.models import Category
from contuga.contrib.transactions.constants import INCOME
from contuga.contrib.transactions.filters import TransactionFilterSet
from contuga.contrib.transactions.models import Transaction

UserModel = get_user_model()


class TransactionFilterTests(TestCase):
    def setUp(self):
        self.data_john = self.create_test_data(name="John")
        self.data_richard = self.create_test_data(name="Richard")
        request_factory = RequestFactory()
        url = reverse("transactions:list")
        self.request = request_factory.get(url)
        self.request.user = self.data_john["user"]

    def create_test_data(self, name):
        user = UserModel.objects.create_user(f"{name}@example.com", "password")
        category = Category.objects.create(
            name=f"{name}'s category", author=user, description="Category description"
        )
        account = Account.objects.create(
            name=f"{name}'s account",
            currency=BGN,
            owner=user,
            description="Account description",
        )
        transaction = Transaction.objects.create(
            amount=100,
            author=user,
            category=category,
            account=account,
            description="Transaction description",
        )

        return {
            "user": user,
            "category": category,
            "account": account,
            "transaction": transaction,
        }

    def test_only_categories_of_current_user_are_shown(self):
        filter = TransactionFilterSet(request=self.request)

        self.assertQuerysetEqual(
            filter.form.fields["category"].queryset,
            self.data_john["user"].categories.all(),
            transform=lambda x: x,
        )

    def test_only_accounts_of_current_user_are_shown(self):
        filter = TransactionFilterSet(request=self.request)

        self.assertQuerysetEqual(
            filter.form.fields["account"].queryset,
            self.data_john["user"].accounts.all(),
            transform=lambda x: x,
        )

    def test_created_at_filter(self):
        transaction = self.data_john["transaction"]
        second_transaction = Transaction.objects.create(
            amount=100,
            type=INCOME,
            author=self.data_john["user"],
            category=self.data_john["category"],
            account=self.data_john["account"],
            description="Second transaction description",
        )

        date_string = transaction.created_at.strftime("%m/%d/%Y")
        data = {"created_at": f"{date_string} - {date_string}"}
        filter = TransactionFilterSet(data=data, request=self.request)

        self.assertListEqual(list(filter.qs), [second_transaction, transaction])

        yesterday = transaction.created_at - timedelta(days=1)
        date_string = yesterday.strftime("%m/%d/%Y")
        data = {"created_at": f"{date_string} - {date_string}"}
        filter = TransactionFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [])

    def test_updated_at_filter(self):
        transaction = self.data_john["transaction"]
        second_transaction = Transaction.objects.create(
            amount=100,
            type=INCOME,
            author=self.data_john["user"],
            category=self.data_john["category"],
            account=self.data_john["account"],
            description="Second transaction description",
        )
        date_string = transaction.updated_at.strftime("%m/%d/%Y")
        data = {"updated_at": f"{date_string} - {date_string}"}
        filter = TransactionFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [second_transaction, transaction])

        yesterday = transaction.updated_at - timedelta(days=1)
        date_string = yesterday.strftime("%m/%d/%Y")
        data = {"updated_at": f"{date_string} - {date_string}"}
        filter = TransactionFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [])
