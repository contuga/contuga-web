from django.conf import settings
from django.test import TestCase

from contuga.contrib.categories.models import Category
from contuga.mixins import TestMixin


class CategorySignalsTests(TestCase, TestMixin):
    def test_signals(self):
        old_categories_count = Category.objects.count()
        user = self.create_user()
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
