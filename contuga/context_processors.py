from django.conf import settings


def tracking(request):
    IS_TRACKING_ENABLED = getattr(settings, "IS_TRACKING_ENABLED", False)
    GOOGLE_TRACKING_CODE = getattr(settings, "GOOGLE_TRACKING_CODE", None)

    return {
        "IS_TRACKING_ENABLED": IS_TRACKING_ENABLED,
        "GOOGLE_TRACKING_CODE": GOOGLE_TRACKING_CODE,
    }
