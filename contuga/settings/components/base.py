"""
Django settings for contuga project.

Generated by 'django-admin startproject' using Django 1.11.18.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

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
    # Django Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps
    "contuga",
    "contuga.contrib.categories.apps.CategoriesConfig",
    "contuga.contrib.transactions.apps.TransactionsConfig",
    "contuga.contrib.analytics.apps.AnalyticsConfig",
    "contuga.contrib.users.apps.UsersConfig",
    "contuga.contrib.accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = "/"

TIME_ZONE = "Europe/Sofia"
USE_TZ = True
