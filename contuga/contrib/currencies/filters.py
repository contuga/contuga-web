from django_filters import filterset

from .models import Currency


class CurrencyFilterSet(filterset.FilterSet):
    class Meta:
        model = Currency
        fields = ("code", "nominal")
