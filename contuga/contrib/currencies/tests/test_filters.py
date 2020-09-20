from django.test import RequestFactory, TestCase
from django.urls import reverse

from contuga.contrib.currencies.filters import CurrencyFilterSet
from contuga.mixins import TestMixin


class CurrencyFilterTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.currency = self.create_currency(code="BGN", nominal=1)
        self.second_currency = self.create_currency(code="JPY", nominal=100)

        request_factory = RequestFactory()
        url = reverse("currencies:list")
        self.request = request_factory.get(url)

    def test_code_filter(self):
        data = {"code": self.currency.code}
        filter = CurrencyFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs,
            self.user.currencies.filter(code=self.currency.code),
            transform=lambda x: x,
        )

        data = {"code": self.second_currency.code}
        filter = CurrencyFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs,
            self.user.currencies.filter(code=self.second_currency.code),
            transform=lambda x: x,
        )

        data = {"code": ""}
        filter = CurrencyFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs, self.user.currencies.all(), transform=lambda x: x
        )

    def test_nominal_filter(self):
        data = {"nominal": self.currency.nominal}
        filter = CurrencyFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs,
            self.user.currencies.filter(nominal=self.currency.nominal),
            transform=lambda x: x,
        )

        data = {"nominal": self.second_currency.nominal}
        filter = CurrencyFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs,
            self.user.currencies.filter(nominal=self.second_currency.nominal),
            transform=lambda x: x,
        )

        data = {"nominal": ""}
        filter = CurrencyFilterSet(data=data, request=self.request)
        self.assertQuerysetEqual(
            filter.qs, self.user.currencies.all(), transform=lambda x: x
        )
