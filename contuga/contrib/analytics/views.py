import json

from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import TemplateView
from django.contrib.auth import mixins

from . import utils


class AnalyticsView(mixins.LoginRequiredMixin, TemplateView):
    template_name = "analytics/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reports = utils.get_monthly_reports(self.request.user)
        context["reports"] = json.dumps(reports, cls=DjangoJSONEncoder)

        return context
