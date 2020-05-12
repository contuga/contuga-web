from django_filters import filterset

from .models import Account


class AccountFilterSet(filterset.FilterSet):
    class Meta:
        model = Account
        fields = ("currency", "is_active")
