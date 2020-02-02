from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^$", views.SettingsDetailView.as_view(), name="detail"),
    re_path(r"^update/$", views.SettingsUpdateView.as_view(), name="update"),
]
