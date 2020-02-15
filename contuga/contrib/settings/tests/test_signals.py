from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Settings

UserModel = get_user_model()


class SettingsSignalsTests(TestCase):
    def test_signals(self):
        old_settings_count = Settings.objects.count()
        user = UserModel.objects.create_user("john.doe@example.com", "password")
        new_settings_count = Settings.objects.count()

        # Assert new settings instance is created
        self.assertEqual(new_settings_count, old_settings_count + 1)

        # Assert settings instance belongs to the correct user
        settings = Settings.objects.last()
        self.assertEqual(settings.user, user)
