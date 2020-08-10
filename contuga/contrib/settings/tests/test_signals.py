from django.test import TestCase

from contuga.mixins import TestMixin

from ..models import Settings


class SettingsSignalsTests(TestCase, TestMixin):
    def test_signals(self):
        old_settings_count = Settings.objects.count()
        user = self.create_user()
        new_settings_count = Settings.objects.count()

        # Assert new settings instance is created
        self.assertEqual(new_settings_count, old_settings_count + 1)

        # Assert settings instance belongs to the correct user
        settings = Settings.objects.last()
        self.assertEqual(settings.user, user)
