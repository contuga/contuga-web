from django.urls import path

from . import views

urlpatterns = [
    path("", views.CategoryListView.as_view(), name="list"),
    path("<int:pk>/", views.CategoryDetailView.as_view(), name="detail"),
    path("new/", views.CategoryCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.CategoryUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="delete"),
]
