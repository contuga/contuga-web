from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from contuga.mixins import TestMixin
from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts import constants as account_constants
from ..models import Transaction
from .. import constants
from . import utils

UserModel = get_user_model()


class TransactionDetailTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.category = Category.objects.create(
            name="Category name", author=self.user, description="Category description"
        )
        self.account = Account.objects.create(
            name="Account name",
            currency=account_constants.BGN,
            owner=self.user,
            description="Account description",
        )
        self.transaction = Transaction.objects.create(
            amount="100.10",
            author=self.user,
            category=self.category,
            account=self.account,
            description="Transaction description",
        )

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def test_get(self):
        url = reverse("transaction-detail", args=[self.transaction.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "type": self.transaction.type,
            "amount": self.transaction.amount,
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[self.category.pk])
            ),
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[self.account.pk])
            ),
            "description": self.transaction.description,
            "updated_at": self.transaction.updated_at.astimezone().isoformat(),
            "created_at": self.transaction.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_transactions_of_other_users(self):
        transaction = utils.create_independent_transaction()

        url = reverse("transaction-detail", args=[transaction.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("transaction-detail", args=[self.transaction.pk])

        category = Category.objects.create(
            name="New category name",
            author=self.user,
            description="New category description",
        )
        account = Account.objects.create(
            name="New account name",
            currency=account_constants.BGN,
            owner=self.user,
            description="New account description",
        )

        data = {
            "type": constants.INCOME,
            "amount": "300.30",
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[account.pk]),
            "description": "New transaction description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        transaction = Transaction.objects.get(pk=self.transaction.pk)

        # Assert transaction is updated
        self.assertNotEqual(transaction.updated_at, self.transaction.updated_at)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "type": data["type"],
            "amount": data["amount"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "description": data["description"],
            "updated_at": transaction.updated_at.astimezone().isoformat(),
            "created_at": self.transaction.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_transactions_of_other_users(self):
        transaction = utils.create_independent_transaction()

        url = reverse("transaction-detail", args=[transaction.pk])

        category = Category.objects.create(
            name="New category name",
            author=self.user,
            description="New category description",
        )
        account = Account.objects.create(
            name="New account name",
            currency=account_constants.BGN,
            owner=self.user,
            description="New account description",
        )

        data = {
            "type": constants.EXPENDITURE,
            "amount": "300.30",
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[account.pk]),
            "description": "New transaction description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        retrieved_transaction = Transaction.objects.get(pk=transaction.pk)

        # Assert transaction is not updated
        self.assertEqual(retrieved_transaction.updated_at, transaction.updated_at)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_patch(self):
        url = reverse("transaction-detail", args=[self.transaction.pk])

        user = UserModel.objects.create_user("richard.roe@example.com", "password")

        data = {
            "author": reverse("user-detail", args=[user.pk]),
            "type": constants.INCOME,
            "amount": "300.30",
            "description": "New transaction description",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        transaction = Transaction.objects.get(pk=self.transaction.pk)

        # Assert transaction is updated
        self.assertNotEqual(transaction.updated_at, self.transaction.updated_at)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "type": data["type"],
            "amount": data["amount"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[self.transaction.category.pk])
            ),
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[self.transaction.account.pk])
            ),
            "description": data["description"],
            "updated_at": transaction.updated_at.astimezone().isoformat(),
            "created_at": self.transaction.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_patch_to_income_with_wrong_category(self):
        category = self.create_category(transaction_type=constants.EXPENDITURE)
        transaction = self.create_transaction(category=category)

        url = reverse("transaction-detail", args=[transaction.pk])

        data = {
            "type": constants.INCOME,
            "amount": transaction.amount,
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[self.account.pk]),
            "description": transaction.description,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 400)

        transaction = Transaction.objects.get(pk=self.transaction.pk)

        # Assert transaction is not updated
        self.assertEqual(transaction.updated_at, self.transaction.updated_at)

        # Assert correct data is returned
        expected_message = _("Invalid hyperlink - Object does not exist.")
        self.assertEqual(response.json(), {"category": [expected_message]})

    def test_patch_to_expenditure_with_wrong_category(self):
        category = self.create_category(transaction_type=constants.INCOME)
        transaction = self.create_transaction(category=category)

        url = reverse("transaction-detail", args=[transaction.pk])

        data = {
            "type": constants.EXPENDITURE,
            "amount": transaction.amount,
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[self.account.pk]),
            "description": transaction.description,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 400)

        transaction = Transaction.objects.get(pk=self.transaction.pk)

        # Assert transaction is updated
        self.assertEqual(transaction.updated_at, self.transaction.updated_at)

        # Assert correct data is returned
        expected_message = _("Invalid hyperlink - Object does not exist.")
        self.assertEqual(response.json(), {"category": [expected_message]})

    def test_delete(self):
        old_transaction_count = Transaction.objects.count()

        url = reverse("transaction-detail", args=[self.transaction.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 204)

        # Assert transaction is deleted
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count - 1)

        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(pk=self.transaction.pk)

    def test_cannot_delete_transactions_of_other_users(self):
        transaction = utils.create_independent_transaction()
        old_transaction_count = Transaction.objects.count()

        url = reverse("transaction-detail", args=[transaction.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert transaction is not deleted
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count)
