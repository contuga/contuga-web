from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import forms, models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    form = forms.CustomUserChangeForm
    add_form = forms.CustomUserCreationForm
    add_form_template = "users/admin_form.html"
    list_display = ("email", "first_name", "last_name", "is_staff")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
