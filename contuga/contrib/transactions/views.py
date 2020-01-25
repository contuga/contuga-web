import json

from django import forms as django_forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy
from django.db import transaction

from import_export.mixins import ExportViewFormMixin

from contuga.contrib.accounts import models as account_models
from contuga.mixins import OnlyAuthoredByCurrentUserMixin
from contuga import views
from . import models, filters, resources, forms, constants


class BaseTransactionFormViewMixin:
    def get_form(self):
        form = super().get_form()
        category_field = form.fields["category"]
        category_field.queryset = category_field.queryset.filter(
            author=self.request.user
        )

        description_field = form.fields["description"]
        description_field.widget = django_forms.Textarea()

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


class InternalTransferFormView(mixins.LoginRequiredMixin, generic.FormView):
    template_name = "transactions/internal_transfer_form.html"
    form_class = forms.InternalTransferForm
    success_url = reverse_lazy("transactions:internal_transfer_success")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        from_account = cleaned_data.get("from_account")
        to_account = cleaned_data.get("to_account")
        amount = cleaned_data.get("amount")

        # TODO: Separate transfers from normal transactions
        session = self.request.session

        expenditure = models.Transaction.objects.create(
            type=constants.EXPENDITURE,
            amount=amount,
            author=self.request.user,
            account=from_account,
        )

        session["expenditure"] = {
            "amount": str(expenditure.amount),
            "currency": expenditure.currency,
            "url": expenditure.get_absolute_url(),
            "account": {
                "name": expenditure.account.name,
                "url": expenditure.account.get_absolute_url(),
            },
        }

        if from_account.currency != to_account.currency:
            amount = amount * cleaned_data.get("rate")

        income = models.Transaction.objects.create(
            type=constants.INCOME,
            amount=amount,
            author=self.request.user,
            account=to_account,
        )

        session["income"] = {
            "amount": str(income.amount),
            "currency": income.currency,
            "url": income.get_absolute_url(),
            "account": {
                "name": income.account.name,
                "url": income.account.get_absolute_url(),
            },
        }

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = account_models.Account.objects.filter(owner=self.request.user)
        accounts_dict = {account.pk: account.currency for account in accounts}
        context["accounts"] = json.dumps(accounts_dict)

        return context


class InternalTransferSuccessView(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "transactions/internal_transfer_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session = self.request.session
        context.update(
            {"expenditure": session.get("expenditure"), "income": session.get("income")}
        )
        self.delete_session_data()
        return context

    def delete_session_data(self):
        session = self.request.session

        if session.get("expenditure"):
            del session["expenditure"]

        if session.get("income"):
            del session["income"]

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context.get("expenditure") and context.get("income"):
            return self.render_to_response(context)
        else:
            return redirect("transactions:internal_transfer_form")
