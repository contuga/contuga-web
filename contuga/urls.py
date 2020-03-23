"""contuga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views import generic
from . import views

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authtoken_views
from rest_framework.documentation import include_docs_urls

from contuga.contrib.transactions.views import TransactionViewSet
from contuga.contrib.accounts.views import AccountViewSet
from contuga.contrib.categories.views import CategoryViewSet
from contuga.contrib.users.views import UserViewSet
from contuga.contrib.settings.views import SettingsViewSet
from contuga.contrib.analytics.views import AnalyticsViewSet


router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"users", UserViewSet, basename="user")
router.register(r"settings", SettingsViewSet, basename="settings")
router.register(r"analytics", AnalyticsViewSet, basename="analytics")

urlpatterns = i18n_patterns(
    path("categories/", include(("contuga.contrib.categories.urls", "categories"))),
    path(
        "transactions/", include(("contuga.contrib.transactions.urls", "transactions"))
    ),
    path("accounts/", include(("contuga.contrib.accounts.urls", "accounts"))),
    path("users/", include(("contuga.contrib.users.urls", "users"))),
    path("settings/", include(("contuga.contrib.settings.urls", "settings"))),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/docs/", include_docs_urls(title="Contuga Web API", public=False)),
    path("api/auth/", include("rest_framework.urls")),
    path("api/token/", authtoken_views.obtain_auth_token),
    path(
        "browserconfig.xml",
        generic.TemplateView.as_view(
            template_name="browserconfig.xml", content_type="text/xml"
        ),
        name="browserconfig",
    ),
    path("manifest.json", views.ManifestView.as_view(), name="manifest"),
    path("analytics", include(("contuga.contrib.analytics.urls", "analytics"))),
    path("", include(("contuga.contrib.pages.urls", "pages"))),
)


if settings.DEBUG:
    import debug_toolbar  # NOQA

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
