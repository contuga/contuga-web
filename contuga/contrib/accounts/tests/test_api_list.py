from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from ..models import Account


class AccountListTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.currency = self.create_currency()
        self.account = self.create_account()

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def create_user_and_account(self, email="richard.roe@example.com"):
        user = self.create_user(email, "password")

        return self.create_account(
            name="Other account name",
            currency=self.currency,
            owner=user,
            description="Other account description",
        )

    def test_get(self):
        url = reverse("account-list")

        # Creating another user and account to make sure the currently
        # logged in user cannot see the accounts of other users
        self.create_user_and_account()

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": response.wsgi_request.build_absolute_uri(
                        reverse("account-detail", args=[self.account.pk])
                    ),
                    "name": self.account.name,
                    "currency": response.wsgi_request.build_absolute_uri(
                        reverse("currency-detail", args=[self.account.currency.pk])
                    ),
                    "owner": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[self.user.pk])
                    ),
                    "description": self.account.description,
                    "is_active": self.account.is_active,
                    "balance": f"{self.account.balance:.2f}",
                    "updated_at": self.account.updated_at.astimezone().isoformat(),
                    "created_at": self.account.created_at.astimezone().isoformat(),
                }
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post(self):
        url = reverse("account-list")

        currency = self.create_currency(name="Euro", code="EUR")

        data = {
            "name": "New account name",
            "currency": reverse("currency-detail", args=[currency.pk]),
            "description": "New account description",
            "is_active": False,
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        account = Account.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "name": account.name,
            "currency": response.wsgi_request.build_absolute_uri(
                reverse("currency-detail", args=[account.currency.pk])
            ),
            "owner": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": account.description,
            "is_active": account.is_active,
            "balance": f"{account.balance:.2f}",
            "updated_at": account.updated_at.astimezone().isoformat(),
            "created_at": account.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_owner_field_is_ignored_on_post(self):
        url = reverse("account-list")
        currency = self.create_currency(name="Euro", code="EUR")
        user = self.create_user(email="richard.roe@example.com", password="password")

        data = {
            "name": "New account name",
            "currency": reverse("currency-detail", args=[currency.pk]),
            "owner": reverse("user-detail", args=[user.pk]),
            "description": "New account description",
            "is_active": False,
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        account = Account.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "name": account.name,
            "currency": response.wsgi_request.build_absolute_uri(
                reverse("currency-detail", args=[account.currency.pk])
            ),
            "owner": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": account.description,
            "is_active": account.is_active,
            "balance": f"{account.balance:.2f}",
            "updated_at": account.updated_at.astimezone().isoformat(),
            "created_at": account.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)
