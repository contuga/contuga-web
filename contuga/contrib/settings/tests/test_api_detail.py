from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.contrib.categories.constants import EXPENDITURE, INCOME
from contuga.mixins import TestMixin

from .. import constants
from ..models import Settings


class SettingsDetailTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.settings = self.user.settings

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def test_get_with_default_values(self):
        url = reverse("settings-detail", args=[self.settings.pk])

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("settings-detail", args=[self.settings.pk])
            ),
            "user": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "default_incomes_category": None,
            "default_expenditures_category": None,
            "default_account": None,
            "transactions_per_page": constants.DEFAULT_TRANSACTIONS_PER_PAGE,
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_with_default_values_changed(self):
        url = reverse("settings-detail", args=[self.settings.pk])

        incomes_category = self.create_category(transaction_type=INCOME)
        expenditures_category = self.create_category(transaction_type=EXPENDITURE)
        currency = self.create_currency()
        account = self.create_account(currency=currency)
        self.settings.default_incomes_category = incomes_category
        self.settings.default_expenditures_category = expenditures_category
        self.settings.default_account = account
        transactions_per_page = self.settings.transactions_per_page + 10
        self.settings.transactions_per_page = transactions_per_page
        self.settings.save()

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("settings-detail", args=[self.settings.pk])
            ),
            "user": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "default_incomes_category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[incomes_category.pk])
            ),
            "default_expenditures_category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[expenditures_category.pk])
            ),
            "default_account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "transactions_per_page": transactions_per_page,
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_settings_of_other_users(self):
        user = self.create_user(email="richard.roe@example.com", password="password")

        url = reverse("settings-detail", args=[user.settings.pk])

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("settings-detail", args=[self.settings.pk])

        incomes_category = self.create_category(transaction_type=INCOME)
        expenditures_category = self.create_category(transaction_type=EXPENDITURE)
        currency = self.create_currency()
        account = self.create_account(currency=currency)

        transactions_per_page = self.settings.transactions_per_page + 10

        data = {
            "default_incomes_category": reverse(
                "category-detail", args=[incomes_category.pk]
            ),
            "default_expenditures_category": reverse(
                "category-detail", args=[expenditures_category.pk]
            ),
            "default_account": reverse("account-detail", args=[account.pk]),
            "transactions_per_page": transactions_per_page,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        settings = Settings.objects.get(pk=self.settings.pk)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("settings-detail", args=[settings.pk])
            ),
            "user": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "default_incomes_category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[incomes_category.pk])
            ),
            "default_expenditures_category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[expenditures_category.pk])
            ),
            "default_account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "transactions_per_page": transactions_per_page,
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_settings_of_other_users(self):
        user = self.create_user(email="richard.roe@example.com", password="password")

        url = reverse("settings-detail", args=[user.settings.pk])

        incomes_category = self.create_category(transaction_type=INCOME)
        expenditures_category = self.create_category(transaction_type=EXPENDITURE)
        currency = self.create_currency()
        account = self.create_account(owner=user, currency=currency)

        data = {
            "default_incomes_category": reverse(
                "category-detail", args=[incomes_category.pk]
            ),
            "default_expenditures_category": reverse(
                "category-detail", args=[expenditures_category.pk]
            ),
            "default_account": reverse("account-detail", args=[account.pk]),
            "transactions_per_page": constants.DEFAULT_TRANSACTIONS_PER_PAGE + 10,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert settings are not updated
        settings = Settings.objects.get(pk=user.pk)

        self.assertEqual(
            user.settings.default_incomes_category, settings.default_incomes_category
        )
        self.assertEqual(
            user.settings.default_expenditures_category,
            settings.default_expenditures_category,
        )
        self.assertEqual(user.settings.default_account, settings.default_account)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_delete_is_not_allowed(self):
        old_settings_count = Settings.objects.count()

        url = reverse("settings-detail", args=[self.settings.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 405)

        # Assert settings is not deleted
        new_settings_count = Settings.objects.count()
        self.assertEqual(new_settings_count, old_settings_count)
