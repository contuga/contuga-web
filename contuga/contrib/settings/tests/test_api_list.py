from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.contrib.categories.constants import EXPENDITURE, INCOME
from contuga.mixins import TestMixin


class SettingsListTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()

        self.settings = self.user.settings

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def test_get_with_default_values(self):
        url = reverse("settings-list")

        # Creating another user to make sure the currently logged in user
        # cannot see the settings of other users
        self.create_user(email="richard.roe@example.com", password="password")

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
                        reverse("settings-detail", args=[self.settings.pk])
                    ),
                    "user": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[self.user.pk])
                    ),
                    "default_incomes_category": None,
                    "default_expenditures_category": None,
                    "default_account": None,
                }
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_with_default_values_changed(self):
        url = reverse("settings-list")

        incomes_category = self.create_category(transaction_type=INCOME)
        expenditures_category = self.create_category(transaction_type=EXPENDITURE)
        account = self.create_account()
        self.settings.default_incomes_category = incomes_category
        self.settings.default_expenditures_category = expenditures_category
        self.settings.default_account = account
        self.settings.save()

        # Creating another user to make sure the currently logged in user
        # cannot see the settings of other users
        self.create_user(email="richard.roe@example.com", password="password")

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
                }
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post_is_not_allowed(self):
        url = reverse("settings-list")

        incomes_category = self.create_category(transaction_type=INCOME)
        expenditures_category = self.create_category(transaction_type=EXPENDITURE)
        account = self.create_account()

        data = {
            "user": reverse("user-detail", args=[self.user.pk]),
            "default_incomes_category": reverse(
                "category-detail", args=[incomes_category.pk]
            ),
            "default_expenditures_category": reverse(
                "category-detail", args=[expenditures_category.pk]
            ),
            "default_account": reverse("account-detail", args=[account.pk]),
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 405)

        # Assert correct data is returned
        expected_response = {"detail": _('Method "POST" not allowed.')}

        self.assertDictEqual(response.json(), expected_response)
