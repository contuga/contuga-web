from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',
        views.TransactionListView.as_view(),
        name='list'),
    url(r'^(?P<pk>\d+)/$',
        views.TransactionDetailView.as_view(),
        name='detail'),
    url(r'^new/$',
        views.TransactionCreateView.as_view(),
        name='create'),
    url(r'^(?P<pk>\d+)/update/$',
        views.TransactionUpdateView.as_view(),
        name='update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.TransactionDeleteView.as_view(),
        name='delete'),
]
