from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "contuga.contrib.accounts"

    def ready(self):
        from . import signals  # NOQA
