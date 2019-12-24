from django import forms
from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy

from import_export.mixins import ExportViewFormMixin

from contuga.mixins import OnlyAuthoredByCurrentUserMixin
from contuga import views
from . import models, filters, resources


class BaseTransactionFormViewMixin:
    def get_form(self):
        form = super().get_form()
        category_field = form.fields["category"]
        category_field.queryset = category_field.queryset.filter(
            author=self.request.user
        )

        description_field = form.fields["description"]
        description_field.widget = forms.Textarea()

        account_field = form.fields["account"]
        account_field.queryset = account_field.queryset.filter(owner=self.request.user)

        return form


class TransactionCreateView(
    BaseTransactionFormViewMixin, mixins.LoginRequiredMixin, generic.CreateView
):
    model = models.Transaction
    fields = ("type", "amount", "account", "category", "description")

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class TransactionListView(
    OnlyAuthoredByCurrentUserMixin,
    mixins.LoginRequiredMixin,
    views.FilteredListView,
    ExportViewFormMixin,
):
    model = models.Transaction
    filterset_class = filters.TransactionFilterSet
    resource_class = resources.TransactionResource
    paginate_by = 50
    success_url = reverse_lazy("transactions:list")


class TransactionDetailView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Transaction


class TransactionUpdateView(
    BaseTransactionFormViewMixin,
    OnlyAuthoredByCurrentUserMixin,
    mixins.LoginRequiredMixin,
    generic.UpdateView,
):
    model = models.Transaction
    fields = ("type", "amount", "account", "category", "description")
    template_name = "transactions/transaction_update_form.html"


class TransactionDeleteView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DeleteView
):
    model = models.Transaction
    success_url = reverse_lazy("transactions:list")
