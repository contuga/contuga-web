from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import mixins

from . import models


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
    fields = ("default_category", "default_account")

    def get_form(self):
        form = super().get_form()

        default_category_field = form.fields["default_category"]
        default_category_field.queryset = default_category_field.queryset.filter(
            author=self.request.user
        )

        default_account_field = form.fields["default_account"]
        default_account_field.queryset = default_account_field.queryset.filter(
            is_active=True, owner=self.request.user
        )

        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())
