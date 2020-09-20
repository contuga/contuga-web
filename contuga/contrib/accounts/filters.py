from django_filters import filters, filterset

from contuga.contrib.currencies import models as currency_models

from .models import Account


def currency_queryset(request):
    if request is None:
        return currency_models.Currency.objects.none()
    return currency_models.Currency.objects.filter(author=request.user)


class AccountFilterSet(filterset.FilterSet):
    currency = filters.ModelChoiceFilter(queryset=currency_queryset)

    class Meta:
        model = Account
        fields = ("is_active",)
