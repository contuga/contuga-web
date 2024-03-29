from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from .. import constants
from ..models import Transaction


class TransactionDetailTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.tags = [self.create_tag(), self.create_tag(name="Second tag")]
        self.tags.reverse()
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.transaction = self.create_transaction(amount="100.10")

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def create_independent_transaction(self):
        user = self.create_user(email="richard.roe@example.com")
        category = self.create_category(author=user)
        tags = [
            self.create_tag(author=user),
            self.create_tag(name="Second tag", author=user),
        ]
        account = self.create_account(owner=user)
        return self.create_expenditure(
            amount="100.10", author=user, category=category, tags=tags, account=account
        )

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
            "tags": [
                response.wsgi_request.build_absolute_uri(
                    reverse("tag-detail", args=[tag.pk])
                )
                for tag in self.tags
            ],
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[self.account.pk])
            ),
            "description": self.transaction.description,
            "expenditure_counterpart": None,
            "updated_at": self.transaction.updated_at.astimezone().isoformat(),
            "created_at": self.transaction.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_transactions_of_other_users(self):
        transaction = self.create_independent_transaction()

        url = reverse("transaction-detail", args=[transaction.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("transaction-detail", args=[self.transaction.pk])

        category = self.create_category(
            name="New category name", description="New category description"
        )
        account = self.create_account(
            name="New account name", description="New account description"
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
            "tags": [
                response.wsgi_request.build_absolute_uri(
                    reverse("tag-detail", args=[tag.pk])
                )
                for tag in self.tags
            ],
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "description": data["description"],
            "expenditure_counterpart": None,
            "updated_at": transaction.updated_at.astimezone().isoformat(),
            "created_at": self.transaction.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_transactions_of_other_users(self):
        transaction = self.create_independent_transaction()

        url = reverse("transaction-detail", args=[transaction.pk])

        category = self.create_category(
            name="New category name", description="New category description"
        )
        account = self.create_account(
            name="New account name", description="New account description"
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

        user = self.create_user(email="richard.roe@example.com", password="password")

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
            "tags": [
                response.wsgi_request.build_absolute_uri(
                    reverse("tag-detail", args=[tag.pk])
                )
                for tag in self.tags
            ],
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[self.transaction.account.pk])
            ),
            "description": data["description"],
            "expenditure_counterpart": None,
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
        transaction = self.create_independent_transaction()
        old_transaction_count = Transaction.objects.count()

        url = reverse("transaction-detail", args=[transaction.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert transaction is not deleted
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count)
