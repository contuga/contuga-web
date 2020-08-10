from django.test import TestCase
from django.urls import reverse

from contuga.contrib.accounts.constants import EUR
from contuga.contrib.settings.models import Settings
from contuga.contrib.transactions.constants import EXPENDITURE, INCOME
from contuga.contrib.transactions.models import Transaction
from contuga.mixins import TestMixin


class TransactionViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.account = self.create_account()
        self.transaction = self.create_transaction()
        self.client.force_login(self.user)

    def test_list(self):
        self.create_account(name="Second account name")
        self.create_account(name="Third account name")
        self.create_account(name="Fourth account name", is_active=False)

        self.create_category(name="Second category name")
        self.create_category(name="Third category name")

        other_user = self.create_user(
            "richard.roe@example.com", "password"
        )
        self.create_category(name="Fourth category name", author=other_user)

        url = reverse("transactions:list")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert queryset is correct
        self.assertQuerysetEqual(
            response.context["transaction_list"],
            Transaction.objects.all(),
            transform=lambda x: x,
        )

    def test_filter_statistics(self):
        eur_account = self.create_account(name="Second account name", currency=EUR)
        income_transaction = self.create_transaction(
            type=INCOME, author=self.user, category=self.category, account=eur_account
        )
        expenditure_transaction = self.create_transaction(
            type=EXPENDITURE,
            author=self.user,
            category=self.category,
            account=eur_account,
        )

        url = reverse("transactions:list")
        response = self.client.get(url, follow=True)

        actual_statistics = response.context["filter_statistics"]

        # Evaluate the currency_statistics to allow comparison later
        actual_statistics["currency_statistics"] = list(
            actual_statistics["currency_statistics"]
        )

        expected_statistics = {
            "transaction_count": self.user.transactions.count(),
            "currency_count": 2,
            "currency_statistics": [
                {
                    "currency": self.account.currency,
                    "income": 0,
                    "expenditure": self.transaction.amount,
                    "balance": -(self.transaction.amount),
                    "count": self.account.transactions.count(),
                },
                {
                    "currency": eur_account.currency,
                    "income": income_transaction.amount,
                    "expenditure": expenditure_transaction.amount,
                    "balance": income_transaction.amount
                    - expenditure_transaction.amount,
                    "count": eur_account.transactions.count(),
                },
            ],
        }

        self.assertEqual(actual_statistics, expected_statistics)

    def test_list_create_form_with_default_settings(self):
        url = reverse("transactions:list")
        response = self.client.get(url, follow=True)

        # Assert initial create form data is correct
        form = response.context.get("create_form")

        category_field = form.fields["category"]
        self.assertEqual(category_field.initial, None)

        account_field = form.fields["account"]
        self.assertEqual(account_field.initial, None)

    def test_list_create_form_with_custom_settings(self):
        settings = Settings.objects.last()
        settings.default_expenditures_category = self.create_category(
            transaction_type=EXPENDITURE
        )
        settings.default_incomes_category = self.create_category(
            transaction_type=INCOME
        )
        settings.default_account = self.account
        settings.save()

        url = reverse("transactions:list")
        response = self.client.get(url, follow=True)

        # Assert initial create form data is correct
        form = response.context.get("create_form")

        category_field = form.fields["category"]
        self.assertEqual(category_field.initial, settings.default_expenditures_category)

        account_field = form.fields["account"]
        self.assertEqual(account_field.initial, settings.default_account)

    def test_detail(self):
        url = reverse("transactions:detail", kwargs={"pk": self.transaction.pk})
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct model is retrieved
        self.assertEqual(response.context["transaction"], self.transaction)

        # Assert transaction fields are used
        fields = [
            self.transaction.amount,
            self.transaction.category.name,
            self.transaction.description,
        ]
        for field in fields:
            self.assertContains(response=response, text=field)

    def test_delete(self):
        old_transaction_count = Transaction.objects.count()

        url = reverse("transactions:delete", kwargs={"pk": self.transaction.pk})
        response = self.client.post(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert transaction is deleted
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count - 1)
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(pk=self.transaction.pk)
