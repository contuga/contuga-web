from .components.base import ROLLBAR

DEBUG = False
EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
IS_TRACKING_ENABLED = True

ROLLBAR["environment"] = "development"
