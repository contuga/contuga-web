from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model

from contuga.contrib.categories.filters import CategoryFilterSet
from contuga.contrib.categories.models import Category
from contuga.contrib.categories.constants import INCOME, EXPENDITURE, ALL

UserModel = get_user_model()


class CategoryFilterTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.income_type_category = Category.objects.create(
            name="Category transaction type INCOME",
            author=self.user,
            transaction_type=INCOME,
            description="First category description",
        )
        self.expenditure_type_category = Category.objects.create(
            name="Category transaction type EXPENDITURE",
            author=self.user,
            transaction_type=EXPENDITURE,
            description="First category description",
        )
        self.all_type_category = Category.objects.create(
            name="Category transaction type ALL",
            author=self.user,
            transaction_type=ALL,
            description="First category description",
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
