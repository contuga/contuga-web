from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from ..models import Currency


class CurrencyDetailTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.currency = self.create_currency()

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def create_user_and_currency(self):
        user = self.create_user(email="richard.roe@example.com", password="password")
        return self.create_currency(author=user)

    def test_get(self):
        url = reverse("currency-detail", args=[self.currency.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": self.currency.name,
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "code": self.currency.code,
            "nominal": self.currency.nominal,
            "updated_at": self.currency.updated_at.astimezone().isoformat(),
            "created_at": self.currency.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_currencies_of_other_users(self):
        currency = self.create_user_and_currency()

        url = reverse("currency-detail", args=[currency.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("currency-detail", args=[self.currency.pk])

        data = {"name": "New currency name", "code": "BGN", "nominal": 1}

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        currency = Currency.objects.get(pk=self.currency.pk)

        # Assert currency is updated
        self.assertNotEqual(currency.updated_at, self.currency.updated_at)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "code": data["code"],
            "nominal": data["nominal"],
            "updated_at": currency.updated_at.astimezone().isoformat(),
            "created_at": self.currency.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_currencies_of_other_users(self):
        currency = self.create_user_and_currency()

        url = reverse("currency-detail", args=[currency.pk])

        data = {"name": "New currency name", "code": "BGN", "nominal": 1}

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        retrieved_currency = Currency.objects.get(pk=currency.pk)

        # Assert currency is not updated
        self.assertEqual(retrieved_currency.updated_at, currency.updated_at)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_patch(self):
        url = reverse("currency-detail", args=[self.currency.pk])

        user = self.create_user(email="richard.roe@example.com", password="password")

        data = {
            "author": reverse("user-detail", args=[user.pk]),
            "name": "New currency name",
            "code": "BGN",
            "nominal": 1,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        currency = Currency.objects.get(pk=self.currency.pk)

        # Assert currency author is not updated
        self.assertEqual(currency.author, self.currency.author)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "code": data["code"],
            "nominal": data["nominal"],
            "updated_at": currency.updated_at.astimezone().isoformat(),
            "created_at": self.currency.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_delete(self):
        old_currency_count = Currency.objects.count()

        url = reverse("currency-detail", args=[self.currency.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 204)

        # Assert currency is deleted
        new_currency_count = Currency.objects.count()
        self.assertEqual(new_currency_count, old_currency_count - 1)

        with self.assertRaises(Currency.DoesNotExist):
            Currency.objects.get(pk=self.currency.pk)

    def test_cannot_delete_currencies_of_other_users(self):
        currency = self.create_user_and_currency()
        old_currency_count = Currency.objects.count()

        url = reverse("currency-detail", args=[currency.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert currency is deleted
        new_currency_count = Currency.objects.count()
        self.assertEqual(new_currency_count, old_currency_count)
