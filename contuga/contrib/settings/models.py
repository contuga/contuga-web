from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.models import Category

UserModel = get_user_model()


class Settings(models.Model):
    user = models.OneToOneField(
        UserModel, related_name="settings", on_delete=models.CASCADE, primary_key=True
    )
    default_incomes_category = models.ForeignKey(
        Category,
        related_name="default_usages_for_incomes",
        on_delete=models.SET_NULL,
        verbose_name=_("Default category for incomes"),
        blank=True,
        null=True,
    )
    default_expenditures_category = models.ForeignKey(
        Category,
        related_name="default_usages_for_expenditures",
        on_delete=models.SET_NULL,
        verbose_name=_("Default category for expenditures"),
        blank=True,
        null=True,
    )
    default_account = models.ForeignKey(
        Account,
        related_name="default_usages",
        on_delete=models.SET_NULL,
        verbose_name=_("Default account"),
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["user"]
        verbose_name = _("User settings")
        verbose_name_plural = _("All user settings")

    def __str__(self):
        return f"Settings of {self.user}"

    def get_absolute_url(self):
        return reverse("settings:detail")
