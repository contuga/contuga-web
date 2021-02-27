from rest_framework import serializers

from .models import Tag


class TagSerializer(serializers.HyperlinkedModelSerializer):
    transactions = serializers.HyperlinkedRelatedField(
        read_only=True, many=True, view_name="transaction-detail"
    )

    class Meta:
        model = Tag
        fields = "__all__"
        extra_kwargs = {
            "author": {"read_only": True},
            "transactions": {"read_only": True},
        }
