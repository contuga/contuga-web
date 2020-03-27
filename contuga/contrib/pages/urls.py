from django.conf.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^$", views.PageRedirectView.as_view(), name="redirect"),
    re_path(r"^home/$", views.HomeView.as_view(), name="home"),
]
