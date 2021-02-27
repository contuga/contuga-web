from django.urls import path

from . import views

urlpatterns = [
    path("", views.TagListView.as_view(), name="list"),
    path("<uuid:pk>/", views.TagDetailView.as_view(), name="detail"),
    path("new/", views.TagCreateView.as_view(), name="create"),
    path("<uuid:pk>/update/", views.TagUpdateView.as_view(), name="update"),
    path("<uuid:pk>/delete/", views.TagDeleteView.as_view(), name="delete"),
]
