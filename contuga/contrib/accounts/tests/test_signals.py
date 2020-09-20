from decimal import Decimal

from django.test import TestCase

from contuga.contrib.transactions import constants as transaction_constants
from contuga.mixins import TestMixin

from ..models import Account


class AccountSignalsTestCase(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.currency = self.create_currency()
        self.account = self.create_account()

    def create_user_and_account(self, email="richard.roe@example.com"):
        user = self.create_user(email, "password")
        currency = self.create_currency()

        return self.create_account(
            name="Other account name",
            currency=currency,
            owner=user,
            description="Other account description",
        )

    def test_balance_update_after_transaction_create(self):
        self.assertEqual(self.account.balance, 0)

        # The following transaction and the signal
        with self.assertNumQueries(2):
            self.create_transaction(
                type=transaction_constants.INCOME, amount=Decimal("100.50")
            )

        # The following transaction and the signal
        with self.assertNumQueries(2):
            self.create_transaction(
                type=transaction_constants.EXPENDITURE, amount=Decimal("50.25")
            )

    def test_balance_update_after_income_transaction_update(self):
        self.assertEqual(self.account.balance, 0)

        income = self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal("100.50")
        )

        # Test with update of income transaction

        with self.assertNumQueries(2):
            income.amount = Decimal("50.50")
            income.save(update_fields=["amount"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, income.amount)

    def test_balance_update_after_expenditure_transaction_update(self):
        self.assertEqual(self.account.balance, 0)

        expenditure = self.create_transaction(
            type=transaction_constants.EXPENDITURE, amount=Decimal("50.25")
        )

        with self.assertNumQueries(2):
            expenditure.amount = Decimal("50.50")
            expenditure.save(update_fields=["amount"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, -expenditure.amount)

    def test_balance_update_after_transaction_type_update_to_income(self):
        self.assertEqual(self.account.balance, 0)

        transaction = self.create_transaction(
            type=transaction_constants.EXPENDITURE, amount=Decimal("50.25")
        )

        with self.assertNumQueries(2):
            transaction.type = transaction_constants.INCOME
            transaction.save(update_fields=["type"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, transaction.amount)

    def test_balance_update_after_transaction_type_update_to_expenditure(self):
        self.assertEqual(self.account.balance, 0)

        transaction = self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal("100.50")
        )

        with self.assertNumQueries(2):
            transaction.type = transaction_constants.EXPENDITURE
            transaction.save(update_fields=["type"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, -transaction.amount)

    def test_balance_update_after_transaction_delete(self):
        income = self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal("100.50")
        )

        expenditure = self.create_transaction(
            type=transaction_constants.EXPENDITURE, amount=Decimal("50.25")
        )

        with self.assertNumQueries(2):
            income.delete()

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, -expenditure.amount)

    def test_balance_update_after_last_transaction_is_deleted(self):
        self.assertEqual(self.account.balance, 0)

        transaction = self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal("100.50")
        )

        with self.assertNumQueries(2):
            transaction.delete()

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, 0)

    def test_balance_update_after_trasaction_account_is_changed(self):
        self.assertEqual(self.account.balance, 0)

        transaction = self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal("100.50")
        )

        second_account = self.create_account(
            name="Second account name", description="Second account description"
        )

        with self.assertNumQueries(2):
            transaction.account = second_account
            transaction.save(update_fields=["account"])

        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, 0)

        second_updated_account = Account.objects.get(pk=second_account.pk)
        self.assertEqual(second_updated_account.balance, transaction.amount)

    def test_unrelated_accounts_are_not_updated(self):
        unrelated_account = self.create_user_and_account()

        transaction = self.create_transaction(
            type=transaction_constants.INCOME, amount=Decimal("100.50")
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

        second_account = self.create_account(
            name="Second account name", description="Second account description"
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
