import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.models import TimestampModel

from . import constants

UserModel = get_user_model()


class Category(TimestampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(_("Name"), max_length=254)
    author = models.ForeignKey(
        UserModel, related_name="categories", on_delete=models.CASCADE
    )
    transaction_type = models.CharField(
        _("Transaction type"),
        max_length=254,
        default=constants.ALL,
        choices=constants.TRANSACTION_TYPE_CHOICES,
        help_text=_("Select which transaction type this category will be used for."),
    )
    description = models.CharField(_("Description"), max_length=1000, blank=True)

    class Meta:
        ordering = ["name", "created_at"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("categories:detail", kwargs={"pk": self.pk})

    def latest_transactions(self, count=20):
        return self.transactions.all()[:count]
