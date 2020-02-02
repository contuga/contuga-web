from django.apps import AppConfig


class SettingsConfig(AppConfig):
    name = "contuga.contrib.settings"

    def ready(self):
        from . import signals  # NOQA
