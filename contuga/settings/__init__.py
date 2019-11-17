"""
This is a django-split-settings main file.

For more information read this:
https://github.com/sobolevn/django-split-settings

Default environment is `developement`.

To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

from split_settings.tools import optional, include
from os import environ

ENV = environ.get("DJANGO_ENV") or "development"

# Include settings:
include(
    "components/base.py",
    "components/static.py",
    "components/internationalization.py",
    "environments/{0}.py".format(ENV),
    optional("environments/local.py"),
)
