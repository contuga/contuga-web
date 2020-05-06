from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from contuga.mixins import TestMixin
from contuga.contrib.transactions.models import Transaction
from contuga.contrib.transactions.constants import INCOME, EXPENDITURE
from contuga.contrib.settings.models import Settings
from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN

UserModel = get_user_model()


class TransactionViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.category = Category.objects.create(
            name="Category name",
            author=self.user,
            transaction_type=EXPENDITURE,
            description="Category description",
        )
        self.account = Account.objects.create(
            name="Account name",
            currency=BGN,
            owner=self.user,
            description="Account description",
        )
        self.transaction = Transaction.objects.create(
            amount=100,
            author=self.user,
            category=self.category,
            account=self.account,
            description="Transaction description",
        )
        self.client.force_login(self.user)

    def test_list(self):
        self.create_account(name="Second account name")
        self.create_account(name="Third account name")
        self.create_account(name="Fourth account name", is_active=False)

        self.create_category(name="Second category name")
        self.create_category(name="Third category name")

        other_user = UserModel.objects.create_user(
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

        # Assert transaction fields are used
        fields = [
            self.transaction.type_icon_class,
            self.transaction.amount,
            self.transaction.category.name,
            self.transaction.description,
        ]
        for field in fields:
            self.assertContains(response=response, text=field)

        # Assert create form is correct
        form = response.context.get("create_form")

        expected_account_queryset = Account.objects.active()
        queryset = form.fields["account"].queryset
        self.assertQuerysetEqual(
            expected_account_queryset, queryset, transform=lambda x: x
        )

        expected_category_queryset = Category.objects.filter(author=self.user)
        queryset = form.fields["category"].queryset
        self.assertQuerysetEqual(
            expected_category_queryset, queryset, transform=lambda x: x
        )

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
