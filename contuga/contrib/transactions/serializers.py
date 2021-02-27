from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        extra_kwargs = {"author": {"read_only": True}, "tags": {"required": False}}
