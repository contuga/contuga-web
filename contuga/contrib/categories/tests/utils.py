from django.contrib.auth import get_user_model

from contuga.contrib.accounts import constants as account_constants
from contuga.contrib.accounts.models import Account
from contuga.contrib.transactions.models import Transaction

from ..models import Category

UserModel = get_user_model()


def create_user_and_category():
    user = UserModel.objects.create_user("richard.roe@example.com", "password")
    return Category.objects.create(
        name="Other category name",
        author=user,
        description="Other category description",
    )


def create_category(user, transaction_type):
    return Category.objects.create(
        name="Category name", transaction_type=transaction_type, author=user
    )


def create_account(user):
    return Account.objects.create(
        name="Account name", currency=account_constants.BGN, owner=user
    )


def create_transaction(category, account):
    return Transaction.objects.create(
        amount=100,
        type=category.transaction_type,
        author=category.author,
        category=category,
        account=account,
        description="Transaction description",
    )
