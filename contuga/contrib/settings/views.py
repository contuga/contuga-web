from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import mixins

from rest_framework import viewsets, permissions

from contuga.contrib.categories import constants as category_constants
from . import models, serializers


class BaseSettingsViewMixin:
    def get_object(self, queryset=None):
        self.kwargs[self.pk_url_kwarg] = getattr(self.request.user, self.pk_url_kwarg)
        return super().get_object(queryset=queryset)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class SettingsDetailView(
    BaseSettingsViewMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Settings


class SettingsUpdateView(
    BaseSettingsViewMixin, mixins.LoginRequiredMixin, generic.UpdateView
):
    model = models.Settings
    fields = (
        "default_incomes_category",
        "default_expenditures_category",
        "default_account",
    )

    def get_form(self):
        form = super().get_form()

        default_incomes_category_field = form.fields["default_incomes_category"]
        default_incomes_category_field.queryset = default_incomes_category_field.queryset.filter(
            author=self.request.user,
            transaction_type__in=[category_constants.ALL, category_constants.INCOME],
        )

        default_expenditures_category_field = form.fields[
            "default_expenditures_category"
        ]
        default_expenditures_category_field.queryset = default_expenditures_category_field.queryset.filter(
            author=self.request.user,
            transaction_type__in=[
                category_constants.ALL,
                category_constants.EXPENDITURE,
            ],
        )

        default_account_field = form.fields["default_account"]
        default_account_field.queryset = default_account_field.queryset.filter(
            owner=self.request.user
        )

        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class SettingsViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SettingsSerializer
    http_method_names = ("get", "put", "patch")

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def get_queryset(self):
        return models.Settings.objects.filter(user=self.request.user)
