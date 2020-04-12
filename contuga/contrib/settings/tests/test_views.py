from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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

    def test_delete(self):
        old_settings_count = Settings.objects.count()
        self.user.delete()
        new_settings_count = Settings.objects.count()

        # Assert settings are deleted
        self.assertEqual(new_settings_count, old_settings_count - 1)
