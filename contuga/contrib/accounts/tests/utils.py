from django.contrib.auth import get_user_model

from ..models import Account
from .. import constants


UserModel = get_user_model()


def create_user_and_account():
    user = UserModel.objects.create_user("richard.roe@example.com", "password")
    return Account.objects.create(
        name="Other account name",
        currency=constants.EUR,
        owner=user,
        description="Other account description",
    )
