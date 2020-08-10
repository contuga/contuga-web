from django.test import RequestFactory, TestCase
from django.urls import reverse

from contuga.mixins import TestMixin
from contuga.contrib.accounts.constants import BGN, EUR
from contuga.contrib.accounts.filters import AccountFilterSet


class AccountFilterTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.first_account = self.create_account(
            name="First account", currency=BGN, description="First account description"
        )

        self.second_account = self.create_account(
            name="Second account",
            currency=EUR,
            description="Second account description",
            is_active=False,
        )

        request_factory = RequestFactory()
        url = reverse("accounts:list")
        self.request = request_factory.get(url)

    def test_is_active_filter(self):
        data = {"is_active": True}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.first_account])

        data = {"is_active": False}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.second_account])

    def test_currency_filter(self):
        data = {"currency": BGN}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.first_account])

        data = {"currency": EUR}
        filter = AccountFilterSet(data=data, request=self.request)
        self.assertListEqual(list(filter.qs), [self.second_account])
