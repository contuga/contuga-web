from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    name = "contuga.contrib.categories"

    def ready(self):
        from . import signals  # NOQA
