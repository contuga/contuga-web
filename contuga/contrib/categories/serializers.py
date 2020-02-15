from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {"author": {"read_only": True}}
