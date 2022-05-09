import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.normpath(os.path.dirname(PROJECT_PATH))

# Media files (file uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = (
    ("bootstrap_scss", os.path.join(BASE_DIR, "node_modules/bootstrap/scss/")),
    ("bootstrap_dist", os.path.join(BASE_DIR, "node_modules/bootstrap/dist/")),
    ("font_awesome_scss", os.path.join(BASE_DIR, "node_modules/font-awesome/scss/")),
    ("chartjs_dist", os.path.join(BASE_DIR, "node_modules/chart.js/dist/")),
    ("daterangepicker", os.path.join(BASE_DIR, "node_modules/daterangepicker")),
    ("tagify_src", os.path.join(BASE_DIR, "node_modules/@yaireo/tagify/src")),
    ("tagify_dist", os.path.join(BASE_DIR, "node_modules/@yaireo/tagify/dist")),
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
                "bootstrap_scss/bootstrap.scss",
                "font_awesome_scss/font-awesome.scss",
                "daterangepicker/daterangepicker.css",
                "tagify_src/tagify.scss",
                "scss/main.scss",
            ),
            "output_filename": "css/main.css",
        }
    },
    "JAVASCRIPT": {
        "main": {
            "source_filenames": (
                "jquery/dist/jquery.js",
                "bootstrap_dist/bootstrap.bundle.js",
                "chartjs_dist/Chart.bundle.js",
                "daterangepicker/moment.min.js",
                "daterangepicker/daterangepicker.js",
                "tagify_dist/tagify.min.js",
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
