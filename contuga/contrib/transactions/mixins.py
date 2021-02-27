import json
from collections import defaultdict

from contuga import utils
from contuga.contrib.categories import constants as category_constants
from contuga.contrib.categories import models as category_models

from . import constants


class BaseTransactionFormViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["category_choices"] = json.dumps(
            self.get_category_choices(self.settings), cls=utils.UUIDEncoder
        )

        return context


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
