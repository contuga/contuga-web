from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from contuga.models import TimestampModel

UserModel = get_user_model()


class Category(TimestampModel):
    name = models.CharField(_("Name"), max_length=254)
    author = models.ForeignKey(
        UserModel, related_name="categories", on_delete=models.CASCADE
    )
    description = models.CharField(_("Description"), max_length=1000, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("categories:detail", kwargs={"pk": self.pk})
