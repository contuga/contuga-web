import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_PATH)

# Media files (file uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "node_modules"),)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "pipeline.finders.PipelineFinder",
)

STATICFILES_STORAGE = "pipeline.storage.PipelineManifestStorage"

# Django Pipeline
# https://django-pipeline.readthedocs.io/en/stable/
PIPELINE = {
    "STYLESHEETS": {
        "main": {
            "source_filenames": (
                "scss/_variables.scss",
                "bootstrap/scss/bootstrap.scss",
                "font-awesome/scss/font-awesome.scss",
                "flatpickr/dist/flatpickr.css",
                "@yaireo/tagify/src/tagify.scss",
                "scss/main.scss",
            ),
            "output_filename": "css/main.css",
        }
    },
    "JAVASCRIPT": {
        "main": {
            "source_filenames": (
                "alpinejs/dist/cdn.js",
                "bootstrap/dist/js/bootstrap.bundle.js",
                "chart.js/dist/Chart.bundle.js",
                "flatpickr/dist/flatpickr.js",
                "flatpickr/dist/l10n/bg.js",
                "@yaireo/tagify/dist/tagify.min.js",
                "js/main.js",
            ),
            "output_filename": "js/main.js",
        }
    },
    "COMPILERS": ("pipeline.compilers.sass.SASSCompiler",),
    "SASS_BINARY": "/usr/bin/env sassc",
    "JS_COMPRESSOR": "pipeline.compressors.uglifyjs.UglifyJSCompressor",
    "CSS_COMPRESSOR": "pipeline.compressors.cssmin.CSSMinCompressor",
}
