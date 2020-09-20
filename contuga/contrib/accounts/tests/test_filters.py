from django.test import RequestFactory, TestCase
from django.urls import reverse

from contuga.contrib.accounts.filters import AccountFilterSet
from contuga.mixins import TestMixin


class AccountFilterTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.first_currency = self.create_currency()
        self.second_currency = self.create_currency(name="Euro", code="EUR")

        self.first_account = self.create_account(
            name="First account",
            currency=self.first_currency,
            description="First account description",
        )

        self.second_account = self.create_account(
            name="Second account",
            currency=self.second_currency,
            description="Second account description",
            is_active=False,
        )

        request_factory = RequestFactory()
        url = reverse("accounts:list")
        self.request = request_factory.get(url)
        self.request.user = self.user

    def test_is_active_filter(self):
        data = {"is_active": True}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.first_account])

        data = {"is_active": False}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.second_account])

    def test_currency_filter(self):
        data = {"currency": self.first_currency.pk}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.first_account])

        data = {"currency": self.second_currency.pk}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.second_account])
