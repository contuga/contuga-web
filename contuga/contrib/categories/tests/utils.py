from django.contrib.auth import get_user_model

from ..models import Category


UserModel = get_user_model()


def create_user_and_category():
    user = UserModel.objects.create_user("richard.roe@example.com", "password")
    return Category.objects.create(
        name="Other category name",
        author=user,
        description="Other category description",
    )
