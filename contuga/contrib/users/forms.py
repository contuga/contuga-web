from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from . import models


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = models.User
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ('email',)
