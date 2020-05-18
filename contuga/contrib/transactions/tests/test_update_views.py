from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.accounts.constants import BGN
from contuga.contrib.accounts.models import Account
from contuga.contrib.transactions.constants import EXPENDITURE, INCOME
from contuga.contrib.transactions.models import Transaction
from contuga.mixins import TestMixin

UserModel = get_user_model()


class TransactionViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.account = Account.objects.create(
            name="Account name",
            currency=BGN,
            owner=self.user,
            description="Account description",
        )
        self.client.force_login(self.user)

    def test_update_get(self):
        category = self.create_category(transaction_type=EXPENDITURE)
        transaction = self.create_transaction(category=category)

        url = reverse("transactions:update", kwargs={"pk": transaction.pk})
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert instance is correct
        instance = response.context.get("object")
        self.assertEqual(instance, transaction)

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
            "type": transaction.type,
            "amount": transaction.amount,
            "category": transaction.category.pk,
            "account": transaction.account.pk,
            "description": transaction.description,
        }
        self.assertDictEqual(form_data, expected_data)

    def test_update(self):
        category = self.create_category(transaction_type=EXPENDITURE)
        transaction = self.create_transaction(category=category)

        new_category = self.create_category(transaction_type=INCOME)
        new_account = Account.objects.create(
            name="Second account name",
            currency=BGN,
            owner=self.user,
            description="Second account description",
        )
        data = {
            "type": INCOME,
            "amount": "300",
            "category": new_category.pk,
            "account": new_account.pk,
            "description": "New transaction description",
        }

        url = reverse("transactions:update", kwargs={"pk": transaction.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("transactions:detail", kwargs={"pk": transaction.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert transaction is updated
        updated_transaction = Transaction.objects.get(pk=transaction.pk)
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
            "pk": transaction.pk,
            "type": INCOME,
            "amount": Decimal("300.00"),
            "author": transaction.author,
            "category": new_category,
            "account": new_account,
            "description": "New transaction description",
        }
        self.assertDictEqual(transaction_data, expected_data)

    def test_update_to_income_with_wrong_category(self):
        category = self.create_category(transaction_type=EXPENDITURE)
        transaction = self.create_transaction(category=category)

        data = {
            "type": INCOME,
            "amount": transaction.amount,
            "category": category.pk,
            "account": self.account.pk,
            "description": transaction.description,
        }

        url = reverse("transactions:update", kwargs={"pk": transaction.pk})
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

        # Assert transaction is not updated
        retrieved_transaction = Transaction.objects.get(pk=transaction.pk)
        transaction_data = {
            "pk": retrieved_transaction.pk,
            "type": retrieved_transaction.type,
            "amount": retrieved_transaction.amount,
            "author": retrieved_transaction.author,
            "category": retrieved_transaction.category,
            "account": retrieved_transaction.account,
            "description": retrieved_transaction.description,
        }
        expected_data = {
            "pk": transaction.pk,
            "type": transaction.type,
            "amount": transaction.amount,
            "author": transaction.author,
            "category": category,
            "account": self.account,
            "description": transaction.description,
        }
        self.assertDictEqual(transaction_data, expected_data)

    def test_update_to_expenditure_with_wrong_category(self):
        category = self.create_category(transaction_type=INCOME)
        transaction = self.create_transaction(category=category, type=INCOME)

        data = {
            "type": EXPENDITURE,
            "amount": transaction.amount,
            "category": category.pk,
            "account": self.account.pk,
            "description": transaction.description,
        }

        url = reverse("transactions:update", kwargs={"pk": transaction.pk})
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

        # Assert transaction is not updated
        retrieved_transaction = Transaction.objects.get(pk=transaction.pk)
        transaction_data = {
            "pk": retrieved_transaction.pk,
            "type": retrieved_transaction.type,
            "amount": retrieved_transaction.amount,
            "author": retrieved_transaction.author,
            "category": retrieved_transaction.category,
            "account": retrieved_transaction.account,
            "description": retrieved_transaction.description,
        }
        expected_data = {
            "pk": transaction.pk,
            "type": transaction.type,
            "amount": transaction.amount,
            "author": transaction.author,
            "category": category,
            "account": self.account,
            "description": transaction.description,
        }
        self.assertDictEqual(transaction_data, expected_data)
