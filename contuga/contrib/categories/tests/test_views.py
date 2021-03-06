from django.test import TestCase
from django.urls import reverse

from contuga.contrib.categories.models import Category
from contuga.mixins import TestMixin

from .. import constants


class CategoryViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.client.force_login(self.user)

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

    def test_create_get(self):
        url = reverse("categories:create")
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        data = {
            "name": "New category name",
            "transaction_type": constants.EXPENDITURE,
            "description": "New category description",
        }
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
        category_data = {
            "name": category.name,
            "transaction_type": constants.EXPENDITURE,
            "description": category.description,
        }
        self.assertDictEqual(category_data, data)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("categories:detail", kwargs={"pk": category.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

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
