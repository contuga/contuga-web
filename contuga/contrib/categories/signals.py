from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Category

UserModel = get_user_model()


@receiver(post_save, sender=UserModel, dispatch_uid="create_user_categories")
def create_user_categories(sender, instance, created, **kwargs):

    if created:
        for category in settings.DEFAULT_CATEGORIES:
            Category.objects.create(name=category, author=instance)
