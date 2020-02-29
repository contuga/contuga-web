from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN
from ..models import Settings

UserModel = get_user_model()


class SettingsDetailTestCase(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
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
            "default_category": None,
            "default_account": None,
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_with_default_values_changed(self):
        url = reverse("settings-detail", args=[self.settings.pk])

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
            "default_category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "default_account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_settings_of_other_users(self):
        user = UserModel.objects.create_user("richard.roe@example.com", "password")

        url = reverse("settings-detail", args=[user.settings.pk])

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("settings-detail", args=[self.settings.pk])

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
            "default_category": reverse("category-detail", args=[category.pk]),
            "default_account": reverse("account-detail", args=[account.pk]),
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
            "default_category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "default_account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_settings_of_other_users(self):
        user = UserModel.objects.create_user("richard.roe@example.com", "password")

        url = reverse("settings-detail", args=[user.settings.pk])

        category = Category.objects.create(
            name="Category name", author=user, description="Category description"
        )
        account = Account.objects.create(
            name="Account name",
            currency=BGN,
            owner=user,
            description="Account description",
        )

        data = {
            "default_category": reverse("category-detail", args=[category.pk]),
            "default_account": reverse("account-detail", args=[account.pk]),
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert settings are not updated
        settings = Settings.objects.get(pk=user.pk)

        self.assertEqual(user.settings.default_category, settings.default_category)
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
