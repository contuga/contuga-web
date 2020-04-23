from datetime import datetime, time

import pytz

from django import forms
from django.utils.translation import ugettext_lazy as _

from django_filters import filters
from django_filters import filterset

from contuga.contrib.accounts import models as account_models
from contuga.contrib.categories import models as category_models
from .models import Transaction
from .forms import TransactionFilterForm


def category_queryset(request):
    if request is None:
        return category_models.Category.objects.none()
    return category_models.Category.objects.filter(author=request.user)


def account_queryset(request):
    if request is None:
        return account_models.Account.objects.none()
    return account_models.Account.objects.filter(owner=request.user)


LOOKUP_CHOICES = (
    ("exact", _("Equals")),
    ("gt", _("Greater than")),
    ("lt", _("Less than")),
)
ORDERING_FIELDS = (
    ("amount", "amount"),
    ("created_at", "created_at"),
    ("updated_at", "updated_at"),
)
ORDERING_LABELS = {
    "amount": _("Amount"),
    "created_at": _("Creation date"),
    "updated_at": _("Last updated"),
}


class TransactionFilterSet(filterset.FilterSet):
    account = filters.ModelChoiceFilter(queryset=account_queryset)
    category = filters.ModelChoiceFilter(queryset=category_queryset)
    created_at = filters.CharFilter(method="filter_by_date_range")
    updated_at = filters.CharFilter(method="filter_by_date_range")
    ordering = filters.OrderingFilter(
        fields=ORDERING_FIELDS, field_labels=ORDERING_LABELS, label=_("Ordering")
    )
    min_amount = filters.NumberFilter(
        field_name="amount", lookup_expr="gte", label=_("Minimum amount")
    )
    max_amount = filters.NumberFilter(
        field_name="amount", lookup_expr="lte", label=_("Maximum amount")
    )
    description = filters.CharFilter(lookup_expr="icontains", label=_("Descripton"))

    class Meta:
        model = Transaction
        fields = ("type",)
        form = TransactionFilterForm

    def filter_by_date_range(self, queryset, name, value):
        if self.form.is_valid():
            start_date, end_date = value.split(" - ")
            date_field = forms.DateField()
            start_datetime = datetime.combine(
                date=date_field.clean(start_date), time=time.min, tzinfo=pytz.UTC
            )
            end_datetime = datetime.combine(
                date=date_field.clean(end_date), time=time.max, tzinfo=pytz.UTC
            )

            queryset = queryset.filter(
                **{
                    "author": self.request.user,
                    f"{name}__gte": start_datetime,
                    f"{name}__lte": end_datetime,
                }
            )

        return queryset
