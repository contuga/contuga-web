from .components.base import ROLLBAR

DEBUG = False
EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
IS_TRACKING_ENABLED = True

ROLLBAR["environment"] = "development"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": database_name,
        "USER": database_user,
        "PASSWORD": database_password,
        "HOST": database_host,
        "PORT": 5432,
    }
}
