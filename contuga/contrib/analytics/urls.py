from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',
        views.AnalyticsView.as_view(),
        name='list'),
]
