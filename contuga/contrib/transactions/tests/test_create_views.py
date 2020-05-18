from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.models import Category
from contuga.contrib.settings.models import Settings
from contuga.contrib.transactions.constants import EXPENDITURE, INCOME
from contuga.contrib.transactions.models import Transaction
from contuga.mixins import TestMixin

UserModel = get_user_model()


class TransactionViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.account = self.create_account()
        self.client.force_login(self.user)

    def test_create_get_with_default_settings(self):
        url = reverse("transactions:create")
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert initial form data is correct
        form = response.context.get("form")

        category_field = form.fields["category"]
        self.assertEqual(category_field.initial, None)

        account_field = form.fields["account"]
        self.assertEqual(account_field.initial, None)

    def test_create_get_with_custom_settings(self):
        settings = Settings.objects.last()
        settings.default_expenditures_category = self.create_category(
            transaction_type=EXPENDITURE
        )
        settings.default_incomes_category = self.create_category(
            transaction_type=INCOME
        )
        settings.default_account = self.account
        settings.save()

        url = reverse("transactions:create")
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert initial form data is correct
        form = response.context.get("form")

        category_field = form.fields["category"]
        self.assertEqual(category_field.initial, settings.default_expenditures_category)

        account_field = form.fields["account"]
        self.assertEqual(account_field.initial, settings.default_account)

    def test_create_get_account_queryset(self):
        self.create_account(name="Second account name")
        self.create_account(name="Third account name")

        # Fourth account should not be in the queryset because it's not active
        self.create_account(name="Fourth account name", is_active=False)

        url = reverse("transactions:create")
        response = self.client.get(url)

        expected_account_queryset = Account.objects.active()

        form = response.context.get("form")
        queryset = form.fields["account"].queryset
        self.assertQuerysetEqual(
            expected_account_queryset, queryset, transform=lambda x: x
        )

    def test_create_get_category_queryset(self):
        self.create_category(name="Second category name")
        self.create_category(name="Third category name")

        other_user = UserModel.objects.create_user(
            "richard.roe@example.com", "password"
        )
        self.create_category(name="Fourth category name", author=other_user)

        url = reverse("transactions:create")
        response = self.client.get(url)

        expected_category_queryset = Category.objects.filter(author=self.user)

        form = response.context.get("form")
        queryset = form.fields["category"].queryset
        self.assertQuerysetEqual(
            expected_category_queryset, queryset, transform=lambda x: x
        )

    def test_create(self):
        category = self.create_category()

        data = {
            "type": EXPENDITURE,
            "amount": "200",
            "author": self.user.pk,
            "category": category.pk,
            "account": self.account.pk,
            "description": "New transaction description",
        }
        old_transaction_count = Transaction.objects.count()

        url = reverse("transactions:create")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert new transaction is created
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count + 1)

        # Assert transaction is saved correctly
        transaction = Transaction.objects.order_by("created_at").last()
        transaction_data = {
            "type": transaction.type,
            "amount": transaction.amount,
            "author": transaction.author,
            "category": transaction.category,
            "account": transaction.account,
            "description": transaction.description,
        }
        expected_data = {
            "type": EXPENDITURE,
            "amount": 200,
            "author": self.user,
            "category": category,
            "account": self.account,
            "description": data["description"],
        }
        self.assertDictEqual(transaction_data, expected_data)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("transactions:detail", kwargs={"pk": transaction.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_create_income_with_wrong_category(self):
        category = self.create_category(transaction_type=EXPENDITURE)

        data = {
            "type": INCOME,
            "amount": "200",
            "author": self.user.pk,
            "category": category.pk,
            "account": self.account.pk,
            "description": "Transaction description",
        }
        old_transaction_count = Transaction.objects.count()

        url = reverse("transactions:create")
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
        self.assertEqual(form.errors, {"category": [expected_message]})

        # Assert new transaction is not created
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count)

    def test_create_expenditure_with_wrong_category(self):
        category = self.create_category(transaction_type=INCOME)

        data = {
            "type": EXPENDITURE,
            "amount": "200",
            "author": self.user.pk,
            "category": category.pk,
            "account": self.account.pk,
            "description": "Transaction description",
        }
        old_transaction_count = Transaction.objects.count()

        url = reverse("transactions:create")
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
        self.assertEqual(form.errors, {"category": [expected_message]})

        # Assert new transaction is not created
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count)
