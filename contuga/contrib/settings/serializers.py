from rest_framework import serializers

from .models import Settings


class SettingsSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name="user-detail")

    class Meta:
        model = Settings
        fields = "__all__"
