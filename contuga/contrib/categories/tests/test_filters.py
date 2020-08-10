from django.test import RequestFactory, TestCase
from django.urls import reverse

from contuga.contrib.categories.constants import ALL, EXPENDITURE, INCOME
from contuga.contrib.categories.filters import CategoryFilterSet
from contuga.mixins import TestMixin


class CategoryFilterTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.income_type_category = self.create_category(
            name="Category transaction type INCOME", transaction_type=INCOME
        )
        self.expenditure_type_category = self.create_category(
            name="Category transaction type EXPENDITURE", transaction_type=EXPENDITURE
        )
        self.all_type_category = self.create_category(
            name="Category transaction type ALL", transaction_type=ALL
        )

        request_factory = RequestFactory()
        url = reverse("categories:list")
        self.request = request_factory.get(url)

    def test_transaction_type_filter(self):
        data = {"transaction_type": INCOME}
        filter = CategoryFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs,
            self.user.categories.filter(transaction_type=INCOME),
            transform=lambda x: x,
        )

        data = {"transaction_type": EXPENDITURE}
        filter = CategoryFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs,
            self.user.categories.filter(transaction_type=EXPENDITURE),
            transform=lambda x: x,
        )

        data = {"transaction_type": ALL}
        filter = CategoryFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs,
            self.user.categories.filter(transaction_type=ALL),
            transform=lambda x: x,
        )

        data = {"transaction_type": ""}
        filter = CategoryFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs, self.user.categories.all(), transform=lambda x: x
        )
