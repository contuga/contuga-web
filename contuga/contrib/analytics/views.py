import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import TemplateView
from django.contrib.auth import mixins

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from . import utils
from .serializers import MonthlyReportSerializer
from .api_filters import MonthlyReportFilterBackend


class AnalyticsView(mixins.LoginRequiredMixin, TemplateView):
    template_name = "analytics/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reports = utils.get_monthly_reports(self.request.user)
        context["reports"] = json.dumps(reports, cls=DjangoJSONEncoder)

        return context


class AnalyticsViewSet(viewsets.ViewSet):
    serlizer_class = MonthlyReportSerializer
    filter_backends = (MonthlyReportFilterBackend,)

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def list(self, request):
        date_field = forms.DateField()
        try:
            start_date = date_field.clean(self.request.query_params.get("start_date"))
        except ValidationError:
            start_date = None

        reports = utils.get_monthly_reports(
            user=self.request.user, start_date=start_date
        )

        serializer = MonthlyReportSerializer(
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
