from django.urls import path

from . import views

urlpatterns = [
    path("", views.SettingsDetailView.as_view(), name="detail"),
    path("update/", views.SettingsUpdateView.as_view(), name="update"),
]
