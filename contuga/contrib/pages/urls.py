from django.urls import path

from . import views

urlpatterns = [
    path("", views.PageRedirectView.as_view(), name="redirect"),
    path("home/", views.HomeView.as_view(), name="home"),
]
