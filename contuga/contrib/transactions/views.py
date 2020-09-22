import json

from django.contrib.auth import mixins
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from import_export.mixins import ExportViewFormMixin
from rest_framework import permissions, viewsets

from contuga import utils, views
from contuga.contrib.accounts import models as account_models
from contuga.contrib.categories import constants as category_constants
from contuga.contrib.settings import models as settings_models
from contuga.mixins import OnlyAuthoredByCurrentUserMixin

from . import constants, filters, forms, models, resources, serializers
from .mixins import BaseTransactionFormViewMixin, GroupedCategoriesMixin


class TransactionCreateView(
    BaseTransactionFormViewMixin,
    GroupedCategoriesMixin,
    mixins.LoginRequiredMixin,
    generic.CreateView,
):
    model = models.Transaction
    fields = ("type", "amount", "account", "category", "description")

    def get_form(self):
        form = super().get_form()

        account_field = form.fields["account"]
        account_field.queryset = account_field.queryset.filter(is_active=True)

        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class TransactionListView(
    GroupedCategoriesMixin,
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

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "account", "account__currency")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TransactionCreateForm(user=self.request.user)
        context["create_form"] = form

        settings = (
            settings_models.Settings.objects.filter(user=self.request.user)
            .select_related(
                "default_expenditures_category",
                "default_incomes_category",
                "default_account",
            )
            .first()
        )
        context["category_choices"] = json.dumps(
            self.get_category_choices(settings), cls=utils.UUIDEncoder
        )
        self.apply_initial_values(form, settings)

        # context["object_list"] cannot be used due to the pagination which makes
        # the use of order_by impossible. Cannot reorder a query once a slice has been taken.
        queryset = self.get_queryset()
        context["filter_statistics"] = self.get_filter_statistics(
            queryset, context.get("paginator")
        )

        return context

    def get_filter_statistics(self, queryset, paginator):
        currency_statistics = (
            queryset.values("account__currency")
            .annotate(
                currency=F("account__currency__name"),
                income=Coalesce(Sum("amount", filter=Q(type="income")), 0),
                expenditure=Coalesce(Sum("amount", filter=Q(type="expenditure")), 0),
                balance=Coalesce(Sum("amount", filter=Q(type="income")), 0)
                - Coalesce(Sum("amount", filter=Q(type="expenditure")), 0),
                count=Count("id"),
            )
            .values("currency", "income", "expenditure", "balance", "count")
            .order_by("currency")
        )

        return {
            "transaction_count": paginator.count,
            "currency_count": len(currency_statistics),
            "currency_statistics": currency_statistics,
        }

    def apply_initial_values(self, form, settings):
        category_field = form.fields["category"]
        category_field.initial = settings.default_expenditures_category

        account_field = form.fields["account"]
        account_field.initial = settings.default_account


class TransactionDetailView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Transaction

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("account", "category", "account__currency")
        )


class TransactionUpdateView(
    BaseTransactionFormViewMixin,
    GroupedCategoriesMixin,
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
        description = cleaned_data.get("description")

        # TODO: Separate transfers from normal transactions
        session = self.request.session

        expenditure = models.Transaction.objects.create(
            type=constants.EXPENDITURE,
            amount=amount,
            author=self.request.user,
            account=from_account,
            description=description,
        )

        session["expenditure"] = {
            "amount": str(expenditure.amount),
            "currency": expenditure.currency.representation,
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
            description=description,
        )

        session["income"] = {
            "amount": str(income.amount),
            "currency": income.currency.representation,
            "url": income.get_absolute_url(),
            "account": {
                "name": income.account.name,
                "url": income.account.get_absolute_url(),
            },
        }

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = account_models.Account.objects.active().filter(
            owner=self.request.user
        )
        accounts_dict = {
            str(account.pk): account.currency.representation for account in accounts
        }
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


class TransactionViewSet(OnlyAuthoredByCurrentUserMixin, viewsets.ModelViewSet):
    serializer_class = serializers.TransactionSerializer
    http_method_names = ("get", "post", "put", "patch", "delete")

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def get_queryset(self):
        return models.Transaction.objects.filter(author=self.request.user)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if self.request.method in ("POST", "PUT", "PATCH"):
            category_field = serializer.fields["category"]

            queryset = category_field.queryset.filter(author=self.request.user)

            if self.request.data.get("type") == constants.INCOME:
                category_field.queryset = queryset.filter(
                    transaction_type__in=[
                        category_constants.ALL,
                        category_constants.INCOME,
                    ]
                )
            else:
                category_field.queryset = queryset.filter(
                    transaction_type__in=[
                        category_constants.ALL,
                        category_constants.EXPENDITURE,
                    ]
                )
        return serializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
