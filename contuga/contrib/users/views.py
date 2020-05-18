from django.conf import settings
from django.contrib.auth import get_user_model, mixins
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django_registration.backends.activation import views as registration_views
from rest_framework import permissions, viewsets

from . import forms
from . import permissions as custom_permissions
from . import serializers

UserModel = get_user_model()


class RegistrationView(registration_views.RegistrationView):
    email_body_template = "users/activation_email_body.txt"
    email_subject_template = "users/activation_email_subject.txt"
    template_name = "users/registration_form.html"
    success_url = reverse_lazy("users:registration_complete")
    disallowed_url = reverse_lazy("users:registration_disallowed")
    form_class = forms.RegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            if redirect_to == self.request.path:
                raise ValueError(
                    _(
                        "Redirection loop for authenticated user detected. "
                        "Check that your LOGIN_REDIRECT_URL doesn't point "
                        "to registration page."
                    )
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_email_context(self, activation_key):
        context = super().get_email_context(activation_key)
        relative_url = reverse("users:activate", args=[activation_key])
        absolute_url = self.request.build_absolute_uri(relative_url)
        context["activation_url"] = absolute_url
        return context


class ActivationView(registration_views.ActivationView):
    template_name = "users/activation_failed.html"
    success_url = reverse_lazy("users:activation_complete")


class LoginView(auth_views.LoginView):
    redirect_authenticated_user = True
    template_name = "users/login.html"


class LogoutView(auth_views.LogoutView):
    pass


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "users/password_change_form.html"
    success_url = reverse_lazy("users:password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "users/password_change_done.html"


class PasswordResetView(auth_views.PasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"


class UserDetailView(mixins.LoginRequiredMixin, generic.DetailView):
    model = UserModel

    def get_queryset(self):
        return super().get_queryset().filter(pk=self.request.user.pk)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    http_method_names = ("get", "post", "put", "patch", "delete")

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method in ("PUT", "PATCH"):
            serializer_class = serializers.UserUpdateSerializer

        return serializer_class

    def get_authenticators(self):
        if self.request.method == "POST":
            return ()

        return super().get_authenticators()

    def get_permissions(self):
        permission_classes = super().get_permissions()

        if self.request.method == "POST":
            permission_classes.append(custom_permissions.IsNotAuthenticated())
        else:
            permission_classes.append(permissions.IsAuthenticated())

            # This is usually not needed because the queryset will prohibit
            # editing other user's data but if the queryset is overrided for
            # whaterver reason this check will also prevent the modification.
            # The queryset will return 404 which is preferred while the lack
            # of permissions will cause 403 revealing the existence of the
            # user.
            permission_classes.append(custom_permissions.IsHimself())

        return permission_classes

    def get_queryset(self):
        return UserModel.objects.filter(pk=self.request.user.pk)
