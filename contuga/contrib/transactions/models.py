import uuid

from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.categories.models import Category
from contuga.models import TimestampModel

from . import constants, managers

UserModel = get_user_model()


class Transaction(TimestampModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
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
        verbose_name=_("Category"),
        blank=True,
        null=True,
    )
    account = models.ForeignKey(
        "accounts.Account",
        related_name="transactions",
        on_delete=models.CASCADE,
        verbose_name=_("Account"),
    )
    expenditure_counterpart = models.OneToOneField(
        "self",
        related_name="income_counterpart",
        on_delete=models.CASCADE,
        verbose_name=_("Expenditure counterpart"),
        blank=True,
        null=True,
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

    def save(self, *args, **kwargs):
        expenditure_condition = (
            self.expenditure_counterpart and self.type == constants.EXPENDITURE
        )

        try:
            income_condition = self.income_counterpart and self.type == constants.INCOME
        except Transaction.DoesNotExist:
            income_condition = False

        if expenditure_condition or income_condition:
            raise ValueError(
                _("Cannot change the type of a transaction that is part of a transfer")
            )

        return super().save(*args, **kwargs)

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

    @property
    def is_part_of_transfer(self):
        try:
            return self.expenditure_counterpart or self.income_counterpart
        except Transaction.DoesNotExist:
            return False

    @property
    def exchange_rate(self):
        if not self.is_part_of_transfer:
            return

        divisible = (
            self.amount if self.is_income else self.income_counterpart.amount
        )

        divisor = self.expenditure_counterpart.amount if self.is_income else self.amount

        return divisible / divisor
