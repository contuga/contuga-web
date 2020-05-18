from django.contrib.auth import get_user_model

from contuga.contrib.accounts import constants as account_constants
from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.models import Category

from ..models import Transaction

UserModel = get_user_model()


def create_independent_transaction():
    user = UserModel.objects.create_user("richard.roe@example.com", "password")
    category = Category.objects.create(
        name="Other category name", author=user, description="Category description"
    )
    account = Account.objects.create(
        name="Other account name",
        currency=account_constants.BGN,
        owner=user,
        description="Other account description",
    )
    return Transaction.objects.create(
        amount="100.10",
        author=user,
        category=category,
        account=account,
        description="Other transaction description",
    )
