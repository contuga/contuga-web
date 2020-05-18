from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserModel
        fields = ("url", "email", "password", "last_login", "date_joined")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserUpdateSerializer(serializers.HyperlinkedModelSerializer):
    current_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = UserModel
        fields = (
            "url",
            "email",
            "last_login",
            "date_joined",
            "current_password",
            "new_password",
        )
        extra_kwargs = {"email": {"read_only": True}}

    def update(self, instance, validated_data):
        new_password = validated_data.get("new_password")
        instance.set_password(new_password)
        instance.save()
        return instance

    def validate_current_password(self, value):
        if not self.instance.check_password(value):
            message = _("Invalid current password")
            raise serializers.ValidationError({"current_password": message})
        return value
