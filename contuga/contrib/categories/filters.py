from django_filters import filterset

from .models import Category


class CategoryFilterSet(filterset.FilterSet):
    class Meta:
        model = Category
        fields = ("transaction_type",)
