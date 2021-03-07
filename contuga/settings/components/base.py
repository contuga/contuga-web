"""
Django settings for contuga project.

Generated by 'django-admin startproject' using Django 1.11.18.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

_ = lambda s: s  # NOQA

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_PATH)

# Media files
# https://docs.djangoproject.com/en/1.11/topics/files/
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

ALLOWED_HOSTS = []
INTERNAL_IPS = ["127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    # Third party apps
    "pipeline",
    "sekizai",
    "widget_tweaks",
    "django_registration",
    "django_extensions",
    "django_filters",
    "anymail",
    "captcha",
    "import_export",
    "rest_framework",
    "rest_framework.authtoken",
    "parler",
    "debug_toolbar",
    # Django Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps
    "contuga",
    "contuga.contrib.pages.apps.PagesConfig",
    "contuga.contrib.categories.apps.CategoriesConfig",
    "contuga.contrib.transactions.apps.TransactionsConfig",
    "contuga.contrib.analytics.apps.AnalyticsConfig",
    "contuga.contrib.users.apps.UsersConfig",
    "contuga.contrib.currencies.apps.CurrenciesConfig",
    "contuga.contrib.accounts.apps.AccountsConfig",
    "contuga.contrib.settings.apps.SettingsConfig",
    "contuga.contrib.tags.apps.TagsConfig",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
]

ROOT_URLCONF = "contuga.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Third party context processors
                "sekizai.context_processors.sekizai",
                # Project context processors
                "contuga.context_processors.tracking",
            ]
        },
    }
]

WSGI_APPLICATION = "contuga.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

AUTH_USER_MODEL = "users.User"
ACCOUNT_ACTIVATION_DAYS = 7

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Authentication
# https://docs.djangoproject.com/en/1.11/topics/auth/default/
# https://django-registration.readthedocs.io/en/3.0.1/
LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "transactions:list"
LOGOUT_REDIRECT_URL = "/"

TIME_ZONE = "Europe/Sofia"
USE_TZ = True

DEFAULT_CATEGORIES = [
    _("Food and drinks"),
    _("Entertainment"),
    _("Bills"),
    _("Transport"),
    _("Drugs and pharmaceuticals"),
    _("Other"),
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "EXCEPTION_HANDLER": "rollbar.contrib.django_rest_framework.post_exception_handler",
}

ROLLBAR = {"access_token": "5887794445d748cb98df0cbed080c9df", "root": BASE_DIR}
