from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.models import TimestampModel

UserModel = get_user_model()


class Currency(TimestampModel):
    name = models.CharField(_("Name"), max_length=254)
    author = models.ForeignKey(
        UserModel, related_name="currencies", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["name", "created_at"]
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("currencies:detail", kwargs={"pk": self.pk})

    def latest_transactions(self, count=20):
        return self.transactions.all()[:count]
