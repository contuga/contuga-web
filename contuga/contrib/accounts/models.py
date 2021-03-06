import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.models import TimestampModel

from . import managers

UserModel = get_user_model()


class Account(TimestampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(_("Name"), max_length=254)
    currency = models.ForeignKey(
        "currencies.Currency",
        related_name="accounts",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        UserModel, related_name="accounts", on_delete=models.CASCADE
    )
    description = models.CharField(_("Description"), max_length=1000, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    balance = models.DecimalField(
        _("Balance"), max_digits=22, decimal_places=2, default=0
    )

    objects = managers.AccountManager()

    class Meta:
        ordering = ["name", "created_at"]
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("accounts:detail", kwargs={"pk": self.pk})

    @property
    def is_balance_positive(self):
        return self.balance > 0

    @property
    def is_balance_negative(self):
        return self.balance < 0

    def latest_transactions(self, count=20):
        return self.transactions.all()[:count]

    def calculate_balance(self, date=None):
        if date:
            queryset = self.transactions.filter(created_at__lte=date)
        else:
            queryset = self.transactions

        return queryset.aggregate(
            balance=Coalesce(Sum("amount", filter=Q(type="income")), 0)
            - Coalesce(Sum("amount", filter=Q(type="expenditure")), 0)
        )["balance"]
