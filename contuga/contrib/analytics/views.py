from django.db.models import Sum
from django.views.generic.base import TemplateView
from django.contrib.auth import mixins

from contuga.contrib.transactions import models


class AnalyticsView(mixins.LoginRequiredMixin, TemplateView):
    template_name = "analytics/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        income = models.Transaction.objects.income().filter(author=self.request.user)
        expenditures = models.Transaction.objects.expenditures().filter(
            author=self.request.user
        )

        income_sum = income.aggregate(Sum("amount"))
        expenditures_sum = expenditures.aggregate(Sum("amount"))

        income_count = len(income)
        expenditures_count = len(expenditures)

        context.update(
            {
                "income_sum": str(income_sum["amount__sum"]),
                "expenditures_sum": str(expenditures_sum["amount__sum"]),
                "income_count": income_count,
                "expenditures_count": expenditures_count,
            }
        )

        return context
