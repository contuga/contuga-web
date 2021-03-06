from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from .. import constants
from ..models import Category


class CategoryDetailTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def create_user_and_category(self):
        user = self.create_user(email="richard.roe@example.com", password="password")
        return self.create_category(author=user)

    def test_get(self):
        url = reverse("category-detail", args=[self.category.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": self.category.name,
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "transaction_type": self.category.transaction_type,
            "description": self.category.description,
            "updated_at": self.category.updated_at.astimezone().isoformat(),
            "created_at": self.category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_categories_of_other_users(self):
        category = self.create_user_and_category()

        url = reverse("category-detail", args=[category.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("category-detail", args=[self.category.pk])

        data = {
            "name": "New category name",
            "transaction_type": constants.EXPENDITURE,
            "description": "New category description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        category = Category.objects.get(pk=self.category.pk)

        # Assert category is updated
        self.assertNotEqual(category.updated_at, self.category.updated_at)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "transaction_type": data["transaction_type"],
            "description": data["description"],
            "updated_at": category.updated_at.astimezone().isoformat(),
            "created_at": self.category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_categories_of_other_users(self):
        category = self.create_user_and_category()

        url = reverse("category-detail", args=[category.pk])

        data = {
            "name": "New category name",
            "transaction_type": constants.EXPENDITURE,
            "description": "New category description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        retrieved_category = Category.objects.get(pk=category.pk)

        # Assert category is not updated
        self.assertEqual(retrieved_category.updated_at, category.updated_at)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_patch(self):
        url = reverse("category-detail", args=[self.category.pk])

        user = self.create_user(email="richard.roe@example.com", password="password")

        data = {
            "author": reverse("user-detail", args=[user.pk]),
            "name": "New category name",
            "transaction_type": constants.EXPENDITURE,
            "description": "New category description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        category = Category.objects.get(pk=self.category.pk)

        # Assert category author is not updated
        self.assertEqual(category.author, self.category.author)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "transaction_type": data["transaction_type"],
            "description": data["description"],
            "updated_at": category.updated_at.astimezone().isoformat(),
            "created_at": self.category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_patch_to_all(self):
        url = reverse("category-detail", args=[self.category.pk])
        currency = self.create_currency()
        account = self.create_account(currency=currency)
        self.create_transaction(account=account)

        data = {
            "name": "New category name",
            "transaction_type": constants.ALL,
            "description": "New category description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        category = Category.objects.get(pk=self.category.pk)

        # Assert category is updated
        self.assertNotEqual(category.updated_at, self.category.updated_at)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "transaction_type": data["transaction_type"],
            "description": data["description"],
            "updated_at": category.updated_at.astimezone().isoformat(),
            "created_at": self.category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_patch_to_income_when_still_in_use(self):
        category = self.create_category(transaction_type=constants.EXPENDITURE)

        url = reverse("category-detail", args=[category.pk])
        currency = self.create_currency()
        account = self.create_account(currency=currency)
        self.create_transaction(category=category, account=account)

        data = {
            "name": "New category name",
            "transaction_type": constants.INCOME,
            "description": "New category description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 400)

        # Assert error is correct
        other_type = _("Expenditure")
        expected_message = _(
            f"This category is still used for transactions of type {other_type}. "
            "Please, fix all transactions before changing the category type."
        )
        self.assertEqual(response.json(), {"transaction_type": [expected_message]})

        retrieved_category = Category.objects.get(pk=category.pk)

        # Assert category is not updated
        self.assertEqual(retrieved_category.updated_at, category.updated_at)

    def test_patch_to_expenditure_when_still_in_use(self):
        category = self.create_category(transaction_type=constants.INCOME)

        url = reverse("category-detail", args=[category.pk])
        currency = self.create_currency()
        account = self.create_account(currency=currency)
        self.create_transaction(
            type=category.transaction_type, category=category, account=account
        )

        data = {
            "name": "New category name",
            "transaction_type": constants.EXPENDITURE,
            "description": "New category description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 400)

        # Assert error is correct
        other_type = _("Income")
        expected_message = _(
            f"This category is still used for transactions of type {other_type}. "
            "Please, fix all transactions before changing the category type."
        )
        self.assertEqual(response.json(), {"transaction_type": [expected_message]})

        retrieved_category = Category.objects.get(pk=category.pk)
        # Assert category is not updated
        self.assertEqual(retrieved_category.updated_at, category.updated_at)

    def test_delete(self):
        old_category_count = Category.objects.count()

        url = reverse("category-detail", args=[self.category.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 204)

        # Assert category is deleted
        new_category_count = Category.objects.count()
        self.assertEqual(new_category_count, old_category_count - 1)

        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=self.category.pk)

    def test_cannot_delete_categories_of_other_users(self):
        category = self.create_user_and_category()
        old_category_count = Category.objects.count()

        url = reverse("category-detail", args=[category.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert category is deleted
        new_category_count = Category.objects.count()
        self.assertEqual(new_category_count, old_category_count)
