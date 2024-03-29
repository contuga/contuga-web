import os

from .components.base import BASE_DIR

DEBUG = True
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
STATICFILES_STORAGE = "pipeline.storage.NonPackagingPipelineStorage"
SECRET_KEY = "SECRET_KEY"
RECAPTCHA_PRIVATE_KEY = "RECAPTCHA_PRIVATE_KEY"
RECAPTCHA_PUBLIC_KEY = "RECAPTCHA_PUBLIC_KEY"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
