from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from ..models import Currency


class CurrencyListTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def test_get(self):
        url = reverse("currency-list")

        # Creating another user and currency to make sure the currently
        # logged in user cannot see the currencies of other users
        user = self.create_user(email="richard.roe@example.com", password="password")
        self.create_currency(author=user)

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        currencies = Currency.objects.filter(author=self.user)

        expected_response = {
            "count": len(currencies),
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": response.wsgi_request.build_absolute_uri(
                        reverse("currency-detail", args=[currency.pk])
                    ),
                    "name": currency.name,
                    "author": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[self.user.pk])
                    ),
                    "code": currency.code,
                    "nominal": currency.nominal,
                    "updated_at": currency.updated_at.astimezone().isoformat(),
                    "created_at": currency.created_at.astimezone().isoformat(),
                }
                for currency in currencies
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post(self):
        url = reverse("currency-list")

        data = {"name": "New currency name", "code": "BGN", "nominal": 1}

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        currency = Currency.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("currency-detail", args=[currency.pk])
            ),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "code": data["code"],
            "nominal": data["nominal"],
            "updated_at": currency.updated_at.astimezone().isoformat(),
            "created_at": currency.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_post(self):
        url = reverse("currency-list")

        user = self.create_user(email="richard.roe@example.com", password="password")

        data = {
            "name": "New currency name",
            "author": reverse("user-detail", args=[user.pk]),
            "code": "BGN",
            "nominal": 1,
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        currency = Currency.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("currency-detail", args=[currency.pk])
            ),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "code": currency.code,
            "nominal": data["nominal"],
            "updated_at": currency.updated_at.astimezone().isoformat(),
            "created_at": currency.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)
