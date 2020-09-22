import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.models import TimestampModel

UserModel = get_user_model()


class Currency(TimestampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(_("Name"), max_length=254)
    code = models.CharField(_("ISO code"), max_length=3, blank=True)
    nominal = models.PositiveSmallIntegerField(_("Nominal"), default=1)
    author = models.ForeignKey(
        UserModel, related_name="currencies", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["name", "code", "created_at"]
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("currencies:detail", kwargs={"pk": self.pk})

    @property
    def representation(self):
        return self.code or self.name

    def latest_transactions(self, count=20):
        return self.transactions.all()[:count]
