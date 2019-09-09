from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^$", views.AccountListView.as_view(), name="list"),
    re_path(r"^(?P<pk>\d+)/$", views.AccountDetailView.as_view(), name="detail"),
    re_path(r"^new/$", views.AccountCreateView.as_view(), name="create"),
    re_path(r"^(?P<pk>\d+)/update/$", views.AccountUpdateView.as_view(), name="update"),
    re_path(r"^(?P<pk>\d+)/delete/$", views.AccountDeleteView.as_view(), name="delete"),
]
