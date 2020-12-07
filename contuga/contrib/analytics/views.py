import json

from django.contrib.auth import mixins
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import TemplateView
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from contuga.contrib.pages import constants
from contuga.contrib.pages.models import Page

from . import utils
from .api_filters import ReportsFilterBackend
from .constants import MONTHS
from .forms import ReportsFilterForm
from .serializers import ReportsSerializer


class AnalyticsView(mixins.LoginRequiredMixin, TemplateView):
    template_name = "analytics/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        reports = None

        if len(self.request.GET):
            form_data = self.request.GET.copy()
            report_unit = form_data.get("report_unit")
            form_data["report_unit"] = report_unit if report_unit else MONTHS
            form = ReportsFilterForm(user, form_data)
        else:
            form = ReportsFilterForm(user)

        if form.is_valid():
            report_unit = form.cleaned_data.get("report_unit")
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")
            category = form.cleaned_data.get("category")

            reports = utils.generate_reports(
                user=user,
                report_unit=report_unit,
                start_date=start_date,
                end_date=end_date,
                category=category,
            )
        else:
            reports = utils.generate_reports(user=user)

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
        user = self.request.user

        if len(self.request.query_params):
            form = ReportsFilterForm(user, self.request.GET)
        else:
            form = ReportsFilterForm(user)

        if form.is_valid():
            report_unit = form.cleaned_data.get("report_unit")
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")
            category = form.cleaned_data.get("category")
            reports = utils.generate_reports(
                user=self.request.user,
                report_unit=report_unit,
                start_date=start_date,
                end_date=end_date,
                category=category,
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
