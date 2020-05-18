from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from contuga.contrib.categories.models import Category

UserModel = get_user_model()


class CategorySignalsTests(TestCase):
    def test_signals(self):
        old_categories_count = Category.objects.count()
        user = UserModel.objects.create_user("john.doe@example.com", "password")
        new_categories_count = Category.objects.count()
        default_categories_len = len(settings.DEFAULT_CATEGORIES)

        # Assert default categories are created
        self.assertEqual(
            new_categories_count, old_categories_count + default_categories_len
        )

        new_categories = Category.objects.order_by("-pk")[:default_categories_len]

        # Assert settings instance belongs to the correct user
        for category in new_categories:
            with self.subTest(category=category.name):
                self.assertEqual(category.author, user)
