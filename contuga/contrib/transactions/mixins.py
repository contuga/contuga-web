import json
from collections import defaultdict

from django import forms as django_forms

from contuga import utils
from contuga.contrib.categories import constants as category_constants
from contuga.contrib.categories import models as category_models

from . import constants


class BaseTransactionFormViewMixin:
    def get_form(self):
        form = super().get_form()
        category_field = form.fields["category"]

        if form.is_bound and form.instance.is_part_of_transfer:
            type_field = form.fields["type"]
            type_field.disabled = True

        queryset = category_field.queryset.filter(author=self.request.user)

        transaction_type = self.request.POST.get("type") if self.request.POST else form.instance.type

        self.update_category_queryset(form, transaction_type, queryset)

        description_field = form.fields["description"]
        description_field.widget = django_forms.Textarea(attrs={"rows": 3})

        account_field = form.fields["account"]
        account_field.queryset = account_field.queryset.filter(owner=self.request.user)

        return form

    def update_category_queryset(self, form, transaction_type, queryset):
        category_field = form.fields["category"]

        if transaction_type == constants.INCOME:
            category_field.queryset = queryset.filter(
                transaction_type__in=(category_constants.ALL, category_constants.INCOME)
            )
        else:
            category_field.queryset = queryset.filter(
                transaction_type__in=(
                    category_constants.ALL,
                    category_constants.EXPENDITURE,
                )
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["category_choices"] = json.dumps(
            self.get_category_choices(self.settings), cls=utils.UUIDEncoder
        )
        self.apply_initial_values(context.get("form"), self.settings)

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
                        "id": str(category.pk),
                        "name": category.name,
                        "selected": category == settings.default_incomes_category,
                    }
                )
            elif category.transaction_type == category_constants.EXPENDITURE:
                grouped_categories[constants.EXPENDITURE].append(
                    {
                        "id": str(category.pk),
                        "name": category.name,
                        "selected": category == settings.default_expenditures_category,
                    }
                )
            else:
                grouped_categories[constants.INCOME].append(
                    {
                        "id": str(category.pk),
                        "name": category.name,
                        "selected": category == settings.default_incomes_category,
                    }
                )
                grouped_categories[constants.EXPENDITURE].append(
                    {
                        "id": str(category.pk),
                        "name": category.name,
                        "selected": category == settings.default_expenditures_category,
                    }
                )

        return grouped_categories
