from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN

UserModel = get_user_model()


class SettingsListTestCase(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")

        self.settings = self.user.settings
        self.client.force_login(self.user)

    def test_get_with_default_values(self):
        url = reverse("settings-list")

        # Creating another user to make sure the currently logged in user
        # cannot see the settings of other users
        UserModel.objects.create_user("richard.roe@example.com", "password")

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
                    "default_category": None,
                    "default_account": None,
                }
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_with_default_values_changed(self):
        url = reverse("settings-list")

        category = Category.objects.create(
            name="Category name", author=self.user, description="Category description"
        )
        account = Account.objects.create(
            name="Account name",
            currency=BGN,
            owner=self.user,
            description="Account description",
        )
        self.settings.default_category = category
        self.settings.default_account = account
        self.settings.save()

        # Creating another user to make sure the currently logged in user
        # cannot see the settings of other users
        UserModel.objects.create_user("richard.roe@example.com", "password")

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
                    "default_category": response.wsgi_request.build_absolute_uri(
                        reverse("category-detail", args=[category.pk])
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

        category = Category.objects.create(
            name="Category name", author=self.user, description="Category description"
        )
        account = Account.objects.create(
            name="Account name",
            currency=BGN,
            owner=self.user,
            description="Account description",
        )

        data = {
            "user": reverse("user-detail", args=[self.user.pk]),
            "default_category": reverse("category-detail", args=[category.pk]),
            "default_account": reverse("account-detail", args=[account.pk]),
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 405)

        # Assert correct data is returned
        expected_response = {"detail": _('Method "POST" not allowed.')}

        self.assertDictEqual(response.json(), expected_response)
