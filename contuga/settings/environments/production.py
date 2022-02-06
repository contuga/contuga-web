from os import environ

from split_settings.tools import include, optional

from .components.base import ROLLBAR

RECAPTCHA_PRIVATE_KEY = environ.get("RECAPTCHA_PRIVATE_KEY") or "RECAPTCHA_PRIVATE_KEY"
RECAPTCHA_PUBLIC_KEY = environ.get("RECAPTCHA_PUBLIC_KEY") or "RECAPTCHA_PUBLIC_KEY"

DEBUG = False
EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
IS_TRACKING_ENABLED = True

ROLLBAR["environment"] = "development"
