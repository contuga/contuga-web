from django.urls import re_path
from django.views.generic import base as base_views

from . import views


urlpatterns = [
    re_path("^login/$", views.LoginView.as_view(), name="login"),
    re_path(r"^logout/$", views.LogoutView.as_view(), name="logout"),
    re_path(r"^register/$", views.RegistrationView.as_view(), name="registration"),
    re_path(
        r"^registration/complete/$",
        base_views.TemplateView.as_view(
            template_name="users/registration_complete.html"
        ),
        name="registration_complete",
    ),
    re_path(
        r"^registration/disallowed/$",
        base_views.TemplateView.as_view(
            template_name="users/registration_disallowed.html"
        ),
        name="registration_disallowed",
    ),
    re_path(
        r"^activate/(?P<activation_key>[-:\w]+)/$",
        views.ActivationView.as_view(),
        name="activate",
    ),
    re_path(
        r"^activation/complete/$",
        base_views.TemplateView.as_view(template_name="users/activation_complete.html"),
        name="activation_complete",
    ),
    re_path(r"^(?P<pk>\d+)/$", views.UserDetailView.as_view(), name="profile"),
    re_path(
        "^password_change/$", views.PasswordChangeView.as_view(), name="password_change"
    ),
    re_path(
        "^password_change/done/$",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    re_path(
        "password_reset/$", views.PasswordResetView.as_view(), name="password_reset"
    ),
    re_path(
        "^password_reset/done/$",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    re_path(
        "^reset/(?P<uidb64>[0-9A-Za-z_-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(
        "^reset/done/$",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
