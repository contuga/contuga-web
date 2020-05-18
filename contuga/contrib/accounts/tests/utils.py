from django.contrib.auth import get_user_model

from .. import constants
from ..models import Account

UserModel = get_user_model()


def create_user_and_account(email="richard.roe@example.com"):
    user = UserModel.objects.create_user(email, "password")
    return Account.objects.create(
        name="Other account name",
        currency=constants.EUR,
        owner=user,
        description="Other account description",
    )
