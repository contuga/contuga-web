from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from contuga.contrib.transactions.models import Transaction
from contuga.contrib.transactions.constants import EXPENDITURE, INCOME
from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.settings.models import Settings
from contuga.contrib.accounts.constants import BGN

UserModel = get_user_model()


class TransactionViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.category = Category.objects.create(
            name="Category name", author=self.user, description="Category description"
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

    def test_create_get(self):
        settings = Settings.objects.last()
        settings.default_category = self.category
        settings.default_account = self.account
        settings.save()

        url = reverse("transactions:create")
        response = self.client.post(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert initial form data is correct
        form = response.context.get("form")

        category_field = form.fields["category"]
        self.assertEqual(category_field.initial, settings.default_category)

        account_field = form.fields["account"]
        self.assertEqual(account_field.initial, settings.default_account)

    def test_create(self):
        data = {
            "type": EXPENDITURE,
            "amount": "200",
            "author": self.user.pk,
            "category": self.category.pk,
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
            "category": self.category,
            "account": self.account,
            "description": "New transaction description",
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

    def test_update_get(self):
        url = reverse("transactions:update", kwargs={"pk": self.transaction.pk})
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert instance is correct
        instance = response.context.get("object")
        self.assertEqual(instance, self.transaction)

        # Assert initial form data is correct
        form = response.context.get("form")
        form_data = {
            "type": form.initial["type"],
            "amount": form.initial["amount"],
            "category": form.initial["category"],
            "account": form.initial["account"],
            "description": form.initial["description"],
        }
        expected_data = {
            "type": self.transaction.type,
            "amount": self.transaction.amount,
            "category": self.transaction.category.pk,
            "account": self.transaction.account.pk,
            "description": self.transaction.description,
        }
        self.assertDictEqual(form_data, expected_data)

    def test_update(self):
        category = Category.objects.create(
            name="Second category name",
            author=self.user,
            description="Second category description",
        )
        account = Account.objects.create(
            name="Second account name",
            currency=BGN,
            owner=self.user,
            description="Second account description",
        )
        data = {
            "type": INCOME,
            "amount": "300",
            "category": category.pk,
            "account": account.pk,
            "description": "New transaction description",
        }

        url = reverse("transactions:update", kwargs={"pk": self.transaction.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("transactions:detail", kwargs={"pk": self.transaction.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert transaction is updated
        updated_transaction = Transaction.objects.get(pk=self.transaction.pk)
        transaction_data = {
            "pk": updated_transaction.pk,
            "type": updated_transaction.type,
            "amount": updated_transaction.amount,
            "author": updated_transaction.author,
            "category": updated_transaction.category,
            "account": updated_transaction.account,
            "description": updated_transaction.description,
        }
        expected_data = {
            "pk": self.transaction.pk,
            "type": INCOME,
            "amount": Decimal("300.00"),
            "author": self.transaction.author,
            "category": category,
            "account": account,
            "description": "New transaction description",
        }
        self.assertDictEqual(transaction_data, expected_data)

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
