from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

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


class CategoryViewTests(TestCase):
    def setUp(self):
        user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.category = Category.objects.create(
            name="Category name", author=user, description="Category description"
        )
        self.client.force_login(user)

    def test_list(self):
        url = reverse("categories:list")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert queryset is correct
        self.assertQuerysetEqual(
            response.context["category_list"],
            Category.objects.all(),
            transform=lambda x: x,
        )

        # Assert category fields are used
        fields = [self.category.name, self.category.description]
        for field in fields:
            self.assertContains(response=response, text=field)

    def test_detail(self):
        url = reverse("categories:detail", kwargs={"pk": self.category.pk})
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct model is retrieved
        self.assertEqual(response.context["category"], self.category)

        # Assert category fields are used
        fields = [self.category.name, self.category.description]
        for field in fields:
            self.assertContains(response=response, text=field)

    def test_create(self):
        data = {"name": "New category name", "description": "New category description"}
        old_category_count = Category.objects.count()

        url = reverse("categories:create")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert new category is created
        new_category_count = Category.objects.count()
        self.assertEqual(new_category_count, old_category_count + 1)

        # Assert category is saved correctly
        category = Category.objects.order_by("created_at").last()
        category_data = {"name": category.name, "description": category.description}
        self.assertDictEqual(category_data, data)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("categories:detail", kwargs={"pk": category.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_update(self):
        data = {"name": "New category name", "description": "New category description"}

        url = reverse("categories:update", kwargs={"pk": self.category.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("categories:detail", kwargs={"pk": self.category.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert category is updated
        updated_category = Category.objects.get(pk=self.category.pk)
        category_data = {
            "name": updated_category.name,
            "description": updated_category.description,
        }
        self.assertDictEqual(category_data, data)

    def test_delete(self):
        old_category_count = Category.objects.count()

        url = reverse("categories:delete", kwargs={"pk": self.category.pk})
        response = self.client.post(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert category is deleted
        new_category_count = Category.objects.count()
        self.assertEqual(new_category_count, old_category_count - 1)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=self.category.pk)
