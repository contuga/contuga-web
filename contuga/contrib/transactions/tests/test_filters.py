import json
from datetime import timedelta

from django.test import RequestFactory, TestCase
from django.urls import reverse

from contuga.contrib.transactions.filters import TransactionFilterSet
from contuga.mixins import TestMixin


class TransactionFilterTests(TestCase, TestMixin):
    def setUp(self):
        self.data_john = self.create_test_data(name="John")
        self.data_richard = self.create_test_data(name="Richard")
        request_factory = RequestFactory()
        url = reverse("transactions:list")
        self.request = request_factory.get(url)
        self.request.user = self.data_john["user"]

    def create_test_data(self, name):
        user = self.create_user(f"{name}@example.com", "password")
        category = self.create_category(author=user, name=f"{name}'s category")
        self.currency = self.create_currency(name=f"{name}'s currency", author=user)

        account = self.create_account(owner=user, name=f"{name}'s account")
        transaction = self.create_transaction(
            author=user, category=category, account=account
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

    def test_tags_filter_with_a_single_tag(self):
        user = self.data_john["user"]
        account = self.data_john["account"]

        first_tag = self.create_tag(name="First tag", author=user)
        second_tag = self.create_tag(name="Second tag", author=user)

        second_transaction = self.create_income(
            author=user, account=account, tags=[first_tag]
        )
        third_transaction = self.create_income(
            author=user, account=account, tags=[first_tag]
        )

        self.create_income(author=user, account=account, tags=[second_tag])

        tags = [{"value": first_tag.name}]
        data = {"tags": json.dumps(tags)}
        filter = TransactionFilterSet(data=data, request=self.request)

        self.assertListEqual(list(filter.qs), [third_transaction, second_transaction])

    def test_tags_filter_with_multiple_tags(self):
        user = self.data_john["user"]
        account = self.data_john["account"]

        first_tag = self.create_tag(name="First tag", author=user)
        second_tag = self.create_tag(name="Second tag", author=user)
        third_tag = self.create_tag(name="Third tag", author=user)

        second_transaction = self.create_income(
            author=user, account=account, tags=[first_tag]
        )
        third_transaction = self.create_income(
            author=user, account=account, tags=[second_tag]
        )

        self.create_income(author=user, account=account, tags=[third_tag])

        tags = [{"value": first_tag.name}, {"value": second_tag.name}]
        data = {"tags": json.dumps(tags)}
        filter = TransactionFilterSet(data=data, request=self.request)

        self.assertListEqual(list(filter.qs), [third_transaction, second_transaction])

    def test_created_at_filter(self):
        transaction = self.data_john["transaction"]
        second_transaction = self.create_income(
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
        second_transaction = self.create_income(
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
