DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
STATICFILES_STORAGE = "pipeline.storage.NonPackagingPipelineStorage"
SECRET_KEY = "SECRET_KEY"
RECAPTCHA_PRIVATE_KEY = "RECAPTCHA_PRIVATE_KEY"
RECAPTCHA_PUBLIC_KEY = "RECAPTCHA_PUBLIC_KEY"
