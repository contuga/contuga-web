from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^$", views.TransactionListView.as_view(), name="list"),
    re_path(r"^(?P<pk>\d+)/$", views.TransactionDetailView.as_view(), name="detail"),
    re_path(
        r"^transfer/$",
        views.InternalTransferFormView.as_view(),
        name="internal_transfer_form",
    ),
    re_path(
        r"^transfer/success$",
        views.InternalTransferSuccessView.as_view(),
        name="internal_transfer_success",
    ),
    re_path(r"^new/$", views.TransactionCreateView.as_view(), name="create"),
    re_path(
        r"^(?P<pk>\d+)/update/$", views.TransactionUpdateView.as_view(), name="update"
    ),
    re_path(
        r"^(?P<pk>\d+)/delete/$", views.TransactionDeleteView.as_view(), name="delete"
    ),
]
