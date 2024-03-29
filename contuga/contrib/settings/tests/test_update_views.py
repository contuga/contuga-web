from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.categories import constants as category_constants
from contuga.mixins import TestMixin

from ..models import Settings


class SettingsViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.settings = Settings.objects.last()
        self.client.force_login(self.user)

        self.currency = self.create_currency()
        self.account = self.create_account()

    def test_update_get(self):
        incomes_category = self.create_category(
            transaction_type=category_constants.INCOME
        )
        expenditures_category = self.create_category(
            transaction_type=category_constants.EXPENDITURE
        )

        self.settings.default_incomes_category = incomes_category
        self.settings.default_expenditures_category = expenditures_category
        self.settings.default_account = self.account
        self.settings.save()

        url = reverse("settings:update")
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert instance is correct
        instance = response.context.get("object")
        self.assertEqual(instance, self.settings)

        # Assert initial form data is correct
        form = response.context.get("form")
        form_data = {
            "default_incomes_category": form.initial["default_incomes_category"],
            "default_expenditures_category": form.initial[
                "default_expenditures_category"
            ],
            "default_account": form.initial["default_account"],
            "transactions_per_page": form.initial["transactions_per_page"],
        }
        expected_data = {
            "default_incomes_category": self.settings.default_incomes_category.pk,
            "default_expenditures_category": self.settings.default_expenditures_category.pk,
            "default_account": self.settings.default_account.pk,
            "transactions_per_page": self.settings.transactions_per_page,
        }
        self.assertDictEqual(form_data, expected_data)

    def test_update(self):
        incomes_category = self.create_category(
            transaction_type=category_constants.INCOME
        )
        expenditures_category = self.create_category(
            transaction_type=category_constants.EXPENDITURE
        )

        transactions_per_page = self.settings.transactions_per_page = 10

        data = {
            "default_incomes_category": incomes_category.pk,
            "default_expenditures_category": expenditures_category.pk,
            "default_account": self.account.pk,
            "transactions_per_page": transactions_per_page,
        }

        url = reverse("settings:update")
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("settings:detail"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert settings are updated
        updated_settings = Settings.objects.get(pk=self.settings.pk)
        settings_data = {
            "pk": updated_settings.pk,
            "default_incomes_category": updated_settings.default_incomes_category,
            "default_expenditures_category": updated_settings.default_expenditures_category,
            "default_account": updated_settings.default_account,
            "transactions_per_page": updated_settings.transactions_per_page,
        }
        expected_data = {
            "pk": self.user.pk,
            "default_incomes_category": incomes_category,
            "default_expenditures_category": expenditures_category,
            "default_account": self.account,
            "transactions_per_page": transactions_per_page,
        }
        self.assertDictEqual(settings_data, expected_data)

    def test_update_with_invalid_default_categories(self):
        incomes_category = self.create_category(
            transaction_type=category_constants.INCOME
        )
        expenditures_category = self.create_category(
            transaction_type=category_constants.EXPENDITURE
        )

        self.settings.default_incomes_category = incomes_category
        self.settings.default_expenditures_category = expenditures_category
        self.settings.default_account = self.account
        self.settings.save()

        data = {
            "default_incomes_category": expenditures_category.pk,
            "default_expenditures_category": incomes_category.pk,
            "default_account": self.account.pk,
            "transactions_per_page": self.settings.transactions_per_page + 10,
        }

        url = reverse("settings:update")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        form = response.context.get("form")

        # Assert form is invalid
        self.assertFalse(form.is_valid())

        # Assert form errors are correct
        expected_message = _(
            "Select a valid choice. That choice is not one of the available choices."
        )
        self.assertEqual(
            form.errors,
            {
                "default_incomes_category": [expected_message],
                "default_expenditures_category": [expected_message],
            },
        )

        # Assert settings are not updated
        updated_settings = Settings.objects.get(pk=self.settings.pk)
        settings_data = {
            "pk": updated_settings.pk,
            "default_incomes_category": updated_settings.default_incomes_category,
            "default_expenditures_category": updated_settings.default_expenditures_category,
            "default_account": updated_settings.default_account,
            "transactions_per_page": updated_settings.transactions_per_page,
        }
        expected_data = {
            "pk": self.settings.pk,
            "default_incomes_category": self.settings.default_incomes_category,
            "default_expenditures_category": self.settings.default_expenditures_category,
            "default_account": self.settings.default_account,
            "transactions_per_page": self.settings.transactions_per_page,
        }
        self.assertDictEqual(settings_data, expected_data)
