from django.urls import path
from . import views

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="list"),
    path("<int:pk>/", views.TransactionDetailView.as_view(), name="detail"),
    path(
        "transfer/",
        views.InternalTransferFormView.as_view(),
        name="internal_transfer_form",
    ),
    path(
        "transfer/success/",
        views.InternalTransferSuccessView.as_view(),
        name="internal_transfer_success",
    ),
    path("new/", views.TransactionCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.TransactionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="delete"),
]
