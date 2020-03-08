from django.utils.translation import ugettext_lazy as _

LEFT = "LEFT"
RIGHT = "RIGHT"

IMAGE_POSITION_CHOICES = ((LEFT, _("Left")), (RIGHT, _("Right")))

HOME_TYPE = "HOME"
ANALYTICS_TYPE = "ANALYTICS"

PAGE_TYPE_CHOICES = ((HOME_TYPE, _("Home")), (ANALYTICS_TYPE, _("Analytics")))
