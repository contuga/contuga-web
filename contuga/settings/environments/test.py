import os

from contuga.settings.components.base import BASE_DIR

SKIP_CAPTCHA = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SECRET_KEY = "SECRET_KEY"
RECAPTCHA_PRIVATE_KEY = "RECAPTCHA_PRIVATE_KEY"
RECAPTCHA_PUBLIC_KEY = "RECAPTCHA_PUBLIC_KEY"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
