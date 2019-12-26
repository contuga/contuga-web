from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core import validators

from . import constants, managers
from contuga.models import TimestampModel
from contuga.contrib.categories.models import Category

UserModel = get_user_model()


class Transaction(TimestampModel):
    type = models.CharField(
        _("Type"),
        max_length=254,
        default=constants.EXPENDITURE,
        choices=constants.TRANSACTION_TYPE_CHOICES,
    )
    amount = models.DecimalField(
        _("Amount"),
        max_digits=12,
        decimal_places=2,
        validators=[validators.MinValueValidator(0)],
    )
    author = models.ForeignKey(
        UserModel, related_name="transactions", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category,
        related_name="transactions",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    account = models.ForeignKey(
        "accounts.Account", related_name="transactions", on_delete=models.CASCADE
    )
    description = models.CharField(_("Description"), max_length=1000, blank=True)

    objects = managers.TransactionManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount}"

    def get_absolute_url(self):
        return reverse("transactions:detail", kwargs={"pk": self.pk})

    @property
    def is_income(self):
        return self.type == constants.INCOME

    @property
    def is_expenditure(self):
        return self.type == constants.EXPENDITURE

    @property
    def type_icon_class(self):
        if self.is_expenditure:
            return "text-danger fa fa-arrow-circle-down"
        else:
            return "text-success fa fa-arrow-circle-up"

    @property
    def currency(self):
        return self.account.currency
