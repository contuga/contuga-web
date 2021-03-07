"""
This is a django-split-settings main file.

For more information read this:
https://github.com/sobolevn/django-split-settings

Default environment is `developement`.

To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

from os import environ

from split_settings.tools import include, optional

ENV = environ.get("DJANGO_ENV") or "development"

# Include settings:
include(
    "components/base.py",
    "components/static.py",
    "components/internationalization.py",
    "components/logging.py",
    "environments/{0}.py".format(ENV),
    optional("environments/local.py"),
)
