from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from contuga.contrib.categories.models import Category
from contuga.contrib.categories import constants
from . import utils

UserModel = get_user_model()


class CategoryViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.client.force_login(self.user)

    def test_update_get(self):
        category = utils.create_category(self.user, constants.ALL)
        url = reverse("categories:update", kwargs={"pk": category.pk})
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert instance is correct
        instance = response.context.get("object")
        self.assertEqual(instance, category)

        # Assert initial form data is correct
        form = response.context.get("form")
        form_data = {
            "name": form.initial["name"],
            "transaction_type": form.initial["transaction_type"],
            "description": form.initial["description"],
        }
        expected_data = {
            "name": category.name,
            "transaction_type": category.transaction_type,
            "description": category.description,
        }
        self.assertDictEqual(form_data, expected_data)

    def test_update(self):
        category = utils.create_category(self.user, constants.ALL)
        data = {
            "name": "New category name",
            "transaction_type": constants.EXPENDITURE,
            "description": "New category description",
        }

        url = reverse("categories:update", kwargs={"pk": category.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("categories:detail", kwargs={"pk": category.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert category is updated
        updated_category = Category.objects.get(pk=category.pk)
        category_data = {
            "name": updated_category.name,
            "transaction_type": updated_category.transaction_type,
            "description": updated_category.description,
        }
        self.assertDictEqual(category_data, data)

    def test_update_to_all(self):
        category = utils.create_category(self.user, constants.EXPENDITURE)
        account = utils.create_account(self.user)
        utils.create_transaction(category=category, account=account)

        data = {
            "name": category.name,
            "transaction_type": constants.ALL,
            "description": category.description,
        }

        url = reverse("categories:update", kwargs={"pk": category.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("categories:detail", kwargs={"pk": category.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert category is updated
        updated_category = Category.objects.get(pk=category.pk)
        category_data = {
            "name": category.name,
            "transaction_type": updated_category.transaction_type,
            "description": category.description,
        }
        self.assertDictEqual(category_data, data)

    def test_update_to_income_when_still_in_use(self):
        category = utils.create_category(self.user, constants.EXPENDITURE)
        account = utils.create_account(self.user)
        utils.create_transaction(category=category, account=account)

        data = {
            "name": category.name,
            "transaction_type": constants.INCOME,
            "description": category.description,
        }

        url = reverse("categories:update", kwargs={"pk": category.pk})
        response = self.client.post(url, data=data, follow=True)

        form = response.context["form"]

        # Assert form is invalid
        self.assertFalse(form.is_valid())

        # Assert form errors are correct
        other_type = _("Expenditure")
        expected_message = _(
            f"This category is still used for transactions of type {other_type}. "
            "Please, fix all transactions before changing the category type."
        )

        self.assertEqual(form.errors, {"transaction_type": [expected_message]})

        # Assert category is not updated
        retrieved_category = Category.objects.get(pk=category.pk)
        self.assertEqual(retrieved_category.updated_at, category.updated_at)

    def test_update_to_expenditure_when_still_in_use(self):
        category = utils.create_category(self.user, constants.INCOME)
        account = utils.create_account(self.user)
        utils.create_transaction(category=category, account=account)

        data = {
            "name": category.name,
            "transaction_type": constants.EXPENDITURE,
            "description": category.description,
        }

        url = reverse("categories:update", kwargs={"pk": category.pk})
        response = self.client.post(url, data=data, follow=True)

        form = response.context["form"]

        # Assert form is invalid
        self.assertFalse(form.is_valid())

        # Assert form errors are correct
        other_type = _("Income")
        expected_message = _(
            f"This category is still used for transactions of type {other_type}. "
            "Please, fix all transactions before changing the category type."
        )

        self.assertEqual(form.errors, {"transaction_type": [expected_message]})

        # Assert category is not updated
        retrieved_category = Category.objects.get(pk=category.pk)
        self.assertEqual(retrieved_category.updated_at, category.updated_at)
