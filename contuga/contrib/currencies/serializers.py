from rest_framework import serializers

from .models import Currency


class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"
        extra_kwargs = {"author": {"read_only": True}}
