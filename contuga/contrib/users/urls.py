from django.urls import re_path, include
from django.views.generic import base as base_views

from . import views


urlpatterns = [
    re_path('^login/$',
            views.LoginView.as_view(),
            name='login'),
    re_path(r'^logout/$',
            views.LogoutView.as_view(),
            name='logout'),
    re_path(r'^register/$',
            views.RegistrationView.as_view(),
            name='registration'),
    re_path(r'^registration/complete/$',
            base_views.TemplateView.as_view(
                template_name='users/registration_complete.html'
            ),
            name='registration_complete'),
    re_path(r'^registration/disallowed/$',
            base_views.TemplateView.as_view(
                template_name='users/registration_disallowed.html'
            ),
            name='registration_disallowed'),
    re_path(r'^activate/(?P<activation_key>[-:\w]+)/$',
            views.ActivationView.as_view(),
            name='activate'),
    re_path(r'^activation/complete/$',
            base_views.TemplateView.as_view(
                template_name='users/activation_complete.html'
            ),
            name='activation_complete'),
    re_path(r'^(?P<pk>\d)/$', views.UserDetailView.as_view(), name='profile'),
    re_path(r'^', include('django.contrib.auth.urls')),
]
