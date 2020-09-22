from django.urls import path

from . import views

urlpatterns = [
    path("", views.CategoryListView.as_view(), name="list"),
    path("<uuid:pk>/", views.CategoryDetailView.as_view(), name="detail"),
    path("new/", views.CategoryCreateView.as_view(), name="create"),
    path("<uuid:pk>/update/", views.CategoryUpdateView.as_view(), name="update"),
    path("<uuid:pk>/delete/", views.CategoryDeleteView.as_view(), name="delete"),
]
