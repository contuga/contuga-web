from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN

from ..models import Settings

UserModel = get_user_model()


class SettingsViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.settings = Settings.objects.last()
        self.client.force_login(self.user)

    def test_detail(self):
        url = reverse("settings:detail")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct model is retrieved
        self.assertEqual(response.context["settings"], self.settings)

    def test_update(self):
        category = Category.objects.create(
            name="Second category name",
            author=self.user,
            description="Second category description",
        )
        account = Account.objects.create(
            name="Second account name",
            currency=BGN,
            owner=self.user,
            description="Second account description",
        )
        data = {"default_category": category.pk, "default_account": account.pk}

        url = reverse("settings:update")
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("settings:detail"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert settings are updated
        updated_settings = Settings.objects.get(pk=self.settings.pk)
        settings_data = {
            "pk": updated_settings.pk,
            "default_category": updated_settings.default_category,
            "default_account": updated_settings.default_account,
        }
        expected_data = {
            "pk": self.user.pk,
            "default_category": category,
            "default_account": account,
        }
        self.assertDictEqual(settings_data, expected_data)

    def test_delete(self):
        old_settings_count = Settings.objects.count()
        self.user.delete()
        new_settings_count = Settings.objects.count()

        # Assert settings are deleted
        self.assertEqual(new_settings_count, old_settings_count - 1)
