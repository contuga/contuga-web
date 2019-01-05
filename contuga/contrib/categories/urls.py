from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',
        views.CategoryListView.as_view(),
        name='list'),
    url(r'^(?P<pk>\d+)/$',
        views.CategoryDetailView.as_view(),
        name='detail'),
    url(r'^new/$',
        views.CategoryCreateView.as_view(),
        name='create'),
    url(r'^(?P<pk>\d+)/update/$',
        views.CategoryUpdateView.as_view(),
        name='update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.CategoryDeleteView.as_view(),
        name='delete'),
]
