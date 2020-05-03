from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from contuga.contrib.transactions.models import Transaction
from contuga.contrib.transactions import constants as transaction_constants
from .utils import create_user_and_account

UserModel = get_user_model()


class AccountSignalsTestCase(TestCase):
    def setUp(self):
        self.account = create_user_and_account()

    def test_balance_update(self):
        self.assertEqual(self.account.balance, 0)

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

        self.assertEqual(self.account.balance, income.amount - expenditure.amount)

        income.amount = Decimal("50.50")
        income.save(update_fields=["amount"])

        expenditure.amount = Decimal("50.50")
        expenditure.save(update_fields=["amount"])

        self.assertEqual(self.account.balance, income.amount - expenditure.amount)

        income.delete()

        self.assertEqual(self.account.balance, -expenditure.amount)
