import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.models import TimestampModel

UserModel = get_user_model()


class Tag(TimestampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(_("Name"), max_length=254)
    author = models.ForeignKey(UserModel, related_name="tags", on_delete=models.CASCADE)

    class Meta:
        ordering = ("name",)
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        unique_together = (("author", "name"),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tags:detail", kwargs={"pk": self.pk})

    def latest_transactions(self, count=20):
        return self.transactions.all()[:count]
