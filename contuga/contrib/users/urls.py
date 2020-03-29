from django.urls import path
from django.views.generic import base as base_views

from . import views


urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegistrationView.as_view(), name="registration"),
    path(
        "registration/complete/",
        base_views.TemplateView.as_view(
            template_name="users/registration_complete.html"
        ),
        name="registration_complete",
    ),
    path(
        "registration/disallowed/",
        base_views.TemplateView.as_view(
            template_name="users/registration_disallowed.html"
        ),
        name="registration_disallowed",
    ),
    path(
        "activate/<str:activation_key>/",
        views.ActivationView.as_view(),
        name="activate",
    ),
    path(
        "activation/complete/",
        base_views.TemplateView.as_view(template_name="users/activation_complete.html"),
        name="activation_complete",
    ),
    path("<int:pk>/", views.UserDetailView.as_view(), name="profile"),
    path(
        "password_change/", views.PasswordChangeView.as_view(), name="password_change"
    ),
    path(
        "password_change/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
