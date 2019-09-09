from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^$", views.CategoryListView.as_view(), name="list"),
    re_path(r"^(?P<pk>\d+)/$", views.CategoryDetailView.as_view(), name="detail"),
    re_path(r"^new/$", views.CategoryCreateView.as_view(), name="create"),
    re_path(
        r"^(?P<pk>\d+)/update/$", views.CategoryUpdateView.as_view(), name="update"
    ),
    re_path(
        r"^(?P<pk>\d+)/delete/$", views.CategoryDeleteView.as_view(), name="delete"
    ),
]
