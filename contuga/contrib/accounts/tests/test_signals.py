from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from contuga.contrib.transactions import constants as transaction_constants
from contuga.contrib.transactions.models import Transaction

from ..models import Account
from .utils import create_user_and_account

UserModel = get_user_model()


class AccountSignalsTestCase(TestCase):
    def setUp(self):
        self.account = create_user_and_account()

    def test_balance_update_after_transaction_create(self):
        self.assertEqual(self.account.balance, 0)

        # The following transaction and the signal
        with self.assertNumQueries(2):
            Transaction.objects.create(
                type=transaction_constants.INCOME,
                amount=Decimal("100.50"),
                author=self.account.owner,
                account=self.account,
            )

        # The following transaction and the signal
        with self.assertNumQueries(2):
            Transaction.objects.create(
                type=transaction_constants.EXPENDITURE,
                amount=Decimal("50.25"),
                author=self.account.owner,
                account=self.account,
            )

    def test_balance_update_after_income_transaction_update(self):
        self.assertEqual(self.account.balance, 0)

        income = Transaction.objects.create(
            type=transaction_constants.INCOME,
            amount=Decimal("100.50"),
            author=self.account.owner,
            account=self.account,
        )

        # Test with update of income transaction

        with self.assertNumQueries(2):
            income.amount = Decimal("50.50")
            income.save(update_fields=["amount"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, income.amount)

    def test_balance_update_after_expenditure_transaction_update(self):
        self.assertEqual(self.account.balance, 0)

        expenditure = Transaction.objects.create(
            type=transaction_constants.EXPENDITURE,
            amount=Decimal("50.25"),
            author=self.account.owner,
            account=self.account,
        )

        with self.assertNumQueries(2):
            expenditure.amount = Decimal("50.50")
            expenditure.save(update_fields=["amount"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, -expenditure.amount)

    def test_balance_update_after_transaction_type_update_to_income(self):
        self.assertEqual(self.account.balance, 0)

        transaction = Transaction.objects.create(
            type=transaction_constants.EXPENDITURE,
            amount=Decimal("50.25"),
            author=self.account.owner,
            account=self.account,
        )

        with self.assertNumQueries(2):
            transaction.type = transaction_constants.INCOME
            transaction.save(update_fields=["type"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, transaction.amount)

    def test_balance_update_after_transaction_type_update_to_expenditure(self):
        self.assertEqual(self.account.balance, 0)

        transaction = Transaction.objects.create(
            type=transaction_constants.INCOME,
            amount=Decimal("100.50"),
            author=self.account.owner,
            account=self.account,
        )

        with self.assertNumQueries(2):
            transaction.type = transaction_constants.EXPENDITURE
            transaction.save(update_fields=["type"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, -transaction.amount)

    def test_balance_update_after_transaction_delete(self):
        income = Transaction.objects.create(
            type=transaction_constants.INCOME,
            amount=Decimal("100.50"),
            author=self.account.owner,
            account=self.account,
        )

        expenditure = Transaction.objects.create(
            type=transaction_constants.EXPENDITURE,
            amount=Decimal("50.25"),
            author=self.account.owner,
            account=self.account,
        )

        with self.assertNumQueries(2):
            income.delete()

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, -expenditure.amount)

    def test_balance_update_after_last_transaction_is_deleted(self):
        self.assertEqual(self.account.balance, 0)

        transaction = Transaction.objects.create(
            type=transaction_constants.INCOME,
            amount=Decimal("100.50"),
            author=self.account.owner,
            account=self.account,
        )

        with self.assertNumQueries(2):
            transaction.delete()

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, 0)

    def test_balance_update_after_trasaction_account_is_changed(self):
        self.assertEqual(self.account.balance, 0)

        transaction = Transaction.objects.create(
            type=transaction_constants.INCOME,
            amount=Decimal("100.50"),
            author=self.account.owner,
            account=self.account,
        )

        second_account = Account.objects.create(
            name="Second account name",
            currency=self.account.currency,
            owner=self.account.owner,
            description="Second account description",
        )

        with self.assertNumQueries(2):
            transaction.account = second_account
            transaction.save(update_fields=["account"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, 0)

        second_updated_account = Account.objects.get(pk=second_account.pk)
        self.assertEqual(second_updated_account.balance, transaction.amount)

    def test_unrelated_accounts_are_not_updated(self):
        unrelated_account = create_user_and_account(email="john.doe@example.com")

        transaction = Transaction.objects.create(
            type=transaction_constants.INCOME,
            amount=Decimal("100.50"),
            author=self.account.owner,
            account=self.account,
        )

        retrieved_unrelated_account = Account.objects.get(pk=unrelated_account.pk)
        self.assertEqual(
            unrelated_account.updated_at, retrieved_unrelated_account.updated_at
        )

        transaction.amount = Decimal("50.50")
        transaction.save(update_fields=["amount"])

        retrieved_unrelated_account = Account.objects.get(pk=unrelated_account.pk)
        self.assertEqual(
            unrelated_account.updated_at, retrieved_unrelated_account.updated_at
        )

        second_account = Account.objects.create(
            name="Second account name",
            currency=self.account.currency,
            owner=self.account.owner,
            description="Second account description",
        )

        with self.assertNumQueries(2):
            transaction.account = second_account
            transaction.save(update_fields=["account"])

        retrieved_unrelated_account = Account.objects.get(pk=unrelated_account.pk)
        self.assertEqual(
            unrelated_account.updated_at, retrieved_unrelated_account.updated_at
        )

        transaction.delete()

        retrieved_unrelated_account = Account.objects.get(pk=unrelated_account.pk)
        self.assertEqual(
            unrelated_account.updated_at, retrieved_unrelated_account.updated_at
        )
