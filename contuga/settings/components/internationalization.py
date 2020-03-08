import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = [("en", "English"), ("bg", "Български")]

LOCALE_PATHS = (os.path.join(PROJECT_PATH, "locale/"),)

USE_I18N = True

USE_L10N = True

# Formatting
# https://docs.djangoproject.com/en/1.11/topics/i18n/formatting/
FORMAT_MODULE_PATH = ["contuga.formats"]
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3


PARLER_LANGUAGES = {None: ({"code": "en"}, {"code": "bg"})}
