from django_filters import rest_framework as filters

from . import models


class TagFilterSet(filters.FilterSet):
    name__startswith = filters.CharFilter(field_name="name", lookup_expr="startswith")

    class Meta:
        model = models.Tag
        fields = ("name", "name__startswith")
