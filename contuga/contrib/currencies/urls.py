from django.urls import path

from . import views

urlpatterns = [
    path("", views.CurrencyListView.as_view(), name="list"),
    path("<int:pk>/", views.CurrencyDetailView.as_view(), name="detail"),
    path("new/", views.CurrencyCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.CurrencyUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.CurrencyDeleteView.as_view(), name="delete"),
]
