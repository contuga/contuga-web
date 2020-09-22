from django.urls import path

from . import views

urlpatterns = [
    path("", views.AccountListView.as_view(), name="list"),
    path("<uuid:pk>/", views.AccountDetailView.as_view(), name="detail"),
    path("new/", views.AccountCreateView.as_view(), name="create"),
    path("<uuid:pk>/update/", views.AccountUpdateView.as_view(), name="update"),
    path("<uuid:pk>/delete/", views.AccountDeleteView.as_view(), name="delete"),
]
