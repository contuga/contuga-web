from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from contuga.contrib.transactions.models import Transaction
from contuga.contrib.transactions import constants as transaction_constants
from . import constants as account_constants
from .models import Account

UserModel = get_user_model()


class AccountsTestCase(TestCase):
    def setUp(self):
        user = UserModel.objects.create_user(email='john.doe@example.com',
                                             password='password')
        self.account = Account.objects.create(name='Account name',
                                              currency=account_constants.BGN,
                                              owner=user)

    def test_balance_property(self):
        self.assertEqual(self.account.balance, 0)

        Transaction.objects.create(type=transaction_constants.INCOME,
                                   amount=Decimal('100.50'),
                                   author=self.account.owner,
                                   account=self.account)

        del self.account.balance
        self.assertEqual(self.account.balance, Decimal('100.50'))

        Transaction.objects.create(type=transaction_constants.EXPENDITURE,
                                   amount=Decimal('50.25'),
                                   author=self.account.owner,
                                   account=self.account)

        del self.account.balance
        self.assertEqual(self.account.balance, Decimal('50.25'))
