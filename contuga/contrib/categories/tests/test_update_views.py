from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.categories import constants
from contuga.contrib.categories.models import Category
from contuga.mixins import TestMixin


class CategoryViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.client.force_login(self.user)

    def test_update_get(self):
        category = self.create_category()
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
        category = self.create_category()
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
        category = self.create_category(transaction_type=constants.EXPENDITURE)
        account = self.create_account()
        self.create_transaction(category=category, account=account)

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
        category = self.create_category(transaction_type=constants.EXPENDITURE)
        account = self.create_account()
        self.create_transaction(
            type=category.transaction_type, category=category, account=account
        )

        data = {
            "name": category.name,
            "transaction_type": constants.INCOME,
            "description": category.description,
        }

        url = reverse("categories:update", kwargs={"pk": category.pk})
        response = self.client.post(url, data=data, follow=True)

        form = response.context.get("form")

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
        category = self.create_category(transaction_type=constants.INCOME)
        account = self.create_account()
        self.create_transaction(
            type=category.transaction_type, category=category, account=account
        )

        data = {
            "name": category.name,
            "transaction_type": constants.EXPENDITURE,
            "description": category.description,
        }

        url = reverse("categories:update", kwargs={"pk": category.pk})
        response = self.client.post(url, data=data, follow=True)

        form = response.context.get("form")

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
