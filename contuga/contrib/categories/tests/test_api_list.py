from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from ..models import Category
from . import utils

UserModel = get_user_model()


class CategoryListTestCase(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.client.force_login(self.user)

    def test_get(self):
        url = reverse("category-list")

        # Creating another user and category to make sure the currently
        # logged in user cannot see the categories of other users
        utils.create_user_and_category()

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        categories = Category.objects.filter(author=self.user)

        expected_response = {
            "count": len(categories),
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": response.wsgi_request.build_absolute_uri(
                        reverse("category-detail", args=[category.pk])
                    ),
                    "name": category.name,
                    "author": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[self.user.pk])
                    ),
                    "description": category.description,
                    "updated_at": category.updated_at.astimezone().isoformat(),
                    "created_at": category.created_at.astimezone().isoformat(),
                }
                for category in categories
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post(self):
        url = reverse("category-list")

        data = {"name": "New category name", "description": "New category description"}

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        category = Category.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": data["description"],
            "updated_at": category.updated_at.astimezone().isoformat(),
            "created_at": category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_post(self):
        url = reverse("category-list")

        user = UserModel.objects.create_user("richard.roe@example.com", "password")

        data = {
            "name": "New category name",
            "author": reverse("user-detail", args=[user.pk]),
            "description": "New category description",
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        category = Category.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": data["description"],
            "updated_at": category.updated_at.astimezone().isoformat(),
            "created_at": category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)
