from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model

from contuga.contrib.accounts.filters import AccountFilterSet
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN, EUR

UserModel = get_user_model()


class AccountFilterTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.first_account = Account.objects.create(
            name="First account",
            currency=BGN,
            owner=self.user,
            description="First account description",
        )
        self.second_account = Account.objects.create(
            name="Second account",
            currency=EUR,
            owner=self.user,
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
