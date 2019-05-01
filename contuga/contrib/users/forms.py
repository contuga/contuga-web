from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from django_registration.forms import RegistrationForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from . import models


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = models.User
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ('email',)


class RegistrationForm(RegistrationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta(RegistrationForm.Meta):
        model = models.User
