from os import environ

database_name = environ.get("DATABASE_NAME") or "contuga"
database_user = environ.get("DATABASE_USER") or "contuga"
database_password = environ.get("DATABASE_PASSWORD") or "contuga"
database_host = "localhost"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
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
