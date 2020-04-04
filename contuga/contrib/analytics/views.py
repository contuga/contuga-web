import json

from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import TemplateView
from django.contrib.auth import mixins

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from contuga.contrib.pages import constants
from contuga.contrib.pages.models import Page
from . import utils
from .forms import ReportsFilterForm
from .constants import MONTHS
from .serializers import ReportsSerializer
from .api_filters import ReportsFilterBackend


class AnalyticsView(mixins.LoginRequiredMixin, TemplateView):
    template_name = "analytics/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reports = None
        if len(self.request.GET):
            form_data = self.request.GET.copy()
            report_unit = form_data.get("report_unit")
            form_data["report_unit"] = report_unit if report_unit else MONTHS
            form = ReportsFilterForm(form_data)
        else:
            form = ReportsFilterForm()

        if form.is_valid():
            report_unit = form.cleaned_data.get("report_unit")
            start_date = form.cleaned_data.get("start_date")
            reports = utils.generate_reports(
                user=self.request.user, report_unit=report_unit, start_date=start_date
            )
        else:
            reports = utils.generate_reports(user=self.request.user)

        if reports:
            context["reports"] = json.dumps(reports, cls=DjangoJSONEncoder)

        context["form"] = form
        context["page"] = Page.objects.filter(type=constants.ANALYTICS_TYPE).first()

        return context


class AnalyticsViewSet(viewsets.ViewSet):
    serlizer_class = ReportsSerializer
    filter_backends = (ReportsFilterBackend,)

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def list(self, request):
        if len(self.request.query_params):
            form = ReportsFilterForm(self.request.GET)
        else:
            form = ReportsFilterForm()

        if form.is_valid():
            report_unit = form.cleaned_data.get("report_unit")
            start_date = form.cleaned_data.get("start_date")
            reports = utils.generate_reports(
                user=self.request.user, report_unit=report_unit, start_date=start_date
            )
        else:
            reports = utils.generate_reports(user=self.request.user)

        serializer = ReportsSerializer(
            instance=reports, many=True, context={"request": request}
        )

        return Response(
            {
                "count": len(reports),
                "next": None,
                "previous": None,
                "results": serializer.data,
            }
        )
