from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django_registration.forms import RegistrationForm

from . import models


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = models.User
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ("email",)


class RegistrationForm(RegistrationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta(RegistrationForm.Meta):
        model = models.User

    def __init__(self, *args, **kwargs):
        if hasattr(settings, "SKIP_CAPTCHA") and self.base_fields.get("captcha"):
            del self.base_fields["captcha"]

        super().__init__(*args, **kwargs)
