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
STATICFILES_DIRS = (
    ("vendor/bootstrap/scss", os.path.join(BASE_DIR, "node_modules/bootstrap/scss/")),
    ("vendor/bootstrap/dist", os.path.join(BASE_DIR, "node_modules/bootstrap/dist/")),
    (
        "vendor/font-awesome/scss",
        os.path.join(BASE_DIR, "node_modules/font-awesome/scss/"),
    ),
    (
        "vendor/font-awesome/fonts",
        os.path.join(BASE_DIR, "node_modules/font-awesome/fonts/"),
    ),
    ("vendor/daterangepicker", os.path.join(BASE_DIR, "node_modules/daterangepicker/")),
    ("vendor/tagify/src", os.path.join(BASE_DIR, "node_modules/@yaireo/tagify/src/")),
    ("vendor/tagify/dist", os.path.join(BASE_DIR, "node_modules/@yaireo/tagify/dist/")),
    ("vendor/jquery/dist", os.path.join(BASE_DIR, "node_modules/jquery/dist/")),
    ("vendor/chart.js/dist", os.path.join(BASE_DIR, "node_modules/chart.js/dist/")),
)

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
                "vendor/bootstrap/scss/bootstrap.scss",
                "vendor/font-awesome/scss/font-awesome.scss",
                "vendor/daterangepicker/daterangepicker.css",
                "vendor/tagify/src/tagify.scss",
                "scss/main.scss",
            ),
            "output_filename": "css/main.css",
        }
    },
    "JAVASCRIPT": {
        "main": {
            "source_filenames": (
                "vendor/jquery/dist/jquery.js",
                "vendor/bootstrap/dist/js/bootstrap.bundle.js",
                "vendor/chart.js/dist/Chart.bundle.js",
                "vendor/daterangepicker/moment.min.js",
                "vendor/daterangepicker/daterangepicker.js",
                "vendor/tagify/dist/tagify.min.js",
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
