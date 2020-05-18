from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Settings

UserModel = get_user_model()


@receiver(post_save, sender=UserModel, dispatch_uid="create_user_settings")
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        Settings.objects.create(user=instance)
