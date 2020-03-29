from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$',
            views.AnalyticsView.as_view(),
            name='list'),
]
