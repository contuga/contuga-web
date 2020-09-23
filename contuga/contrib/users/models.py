import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    username = models.CharField(
        _("Username"),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_("150 characters or fewer. " "Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={"unique": _("A user with that username already exists.")},
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email
