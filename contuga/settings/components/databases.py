from os import environ

from split_settings.tools import include, optional

database_name = environ.get("DATABASE_NAME") or "contuga"
database_user = environ.get("DATABASE_USER") or "contuga"
database_password = environ.get("DATABASE_PASSWORD") or "contuga"
database_host = "localhost"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
