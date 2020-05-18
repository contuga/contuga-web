import json
from collections import defaultdict

from django import forms as django_forms

from contuga.contrib.categories import constants as category_constants
from contuga.contrib.categories import models as category_models
from contuga.contrib.settings import models as settings_models

from . import constants


class BaseTransactionFormViewMixin:
    def get_form(self):
        form = super().get_form()
        category_field = form.fields["category"]

        queryset = category_field.queryset.filter(author=self.request.user)

        if self.request.POST:
            if self.request.POST.get("type") == constants.INCOME:
                category_field.queryset = queryset.filter(
                    transaction_type__in=(
                        category_constants.ALL,
                        category_constants.INCOME,
                    )
                )
            else:
                category_field.queryset = queryset.filter(
                    transaction_type__in=(
                        category_constants.ALL,
                        category_constants.EXPENDITURE,
                    )
                )
        else:
            if form.instance.type == constants.INCOME:
                category_field.queryset = queryset.filter(
                    transaction_type__in=(
                        category_constants.ALL,
                        category_constants.INCOME,
                    )
                )
            else:
                category_field.queryset = queryset.filter(
                    transaction_type__in=[
                        category_constants.ALL,
                        category_constants.EXPENDITURE,
                    ]
                )

        description_field = form.fields["description"]
        description_field.widget = django_forms.Textarea(attrs={"rows": 3})

        account_field = form.fields["account"]
        account_field.queryset = account_field.queryset.filter(owner=self.request.user)

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        settings = (
            settings_models.Settings.objects.filter(user=self.request.user)
            .select_related(
                "default_expenditures_category",
                "default_incomes_category",
                "default_account",
            )
            .first()
        )
        context["category_choices"] = json.dumps(self.get_category_choices(settings))
        self.apply_initial_values(context.get("form"), settings)

        return context

    def apply_initial_values(self, form, settings):
        category_field = form.fields["category"]
        category_field.initial = settings.default_expenditures_category

        account_field = form.fields["account"]
        account_field.initial = settings.default_account


class GroupedCategoriesMixin:
    def get_category_choices(self, settings):
        categories = category_models.Category.objects.filter(author=self.request.user)

        grouped_categories = defaultdict(list)
        for category in categories:
            if category.transaction_type == category_constants.INCOME:
                grouped_categories[constants.INCOME].append(
                    {
                        "id": category.pk,
                        "name": category.name,
                        "selected": category == settings.default_incomes_category,
                    }
                )
            elif category.transaction_type == category_constants.EXPENDITURE:
                grouped_categories[constants.EXPENDITURE].append(
                    {
                        "id": category.pk,
                        "name": category.name,
                        "selected": category == settings.default_expenditures_category,
                    }
                )
            else:
                grouped_categories[constants.INCOME].append(
                    {
                        "id": category.pk,
                        "name": category.name,
                        "selected": category == settings.default_incomes_category,
                    }
                )
                grouped_categories[constants.EXPENDITURE].append(
                    {
                        "id": category.pk,
                        "name": category.name,
                        "selected": category == settings.default_expenditures_category,
                    }
                )

        return grouped_categories
