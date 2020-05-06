import json
from collections import defaultdict

from django import forms as django_forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy
from django.db import transaction

from import_export.mixins import ExportViewFormMixin
from rest_framework import viewsets, permissions

from contuga.contrib.accounts import models as account_models
from contuga.contrib.categories import (
    constants as category_constants,
    models as category_models,
)
from contuga.contrib.settings import models as settings_models
from contuga.mixins import OnlyAuthoredByCurrentUserMixin
from contuga import views
from . import models, filters, resources, forms, constants, serializers


class BaseTransactionFormViewMixin:
    def get_form(self):
        form = super().get_form()
        category_field = form.fields["category"]

        queryset = category_field.queryset.filter(author=self.request.user)

        if self.request.POST and self.request.POST.get("type") == constants.INCOME:
            category_field.queryset = queryset.filter(
                transaction_type__in=(category_constants.ALL, category_constants.INCOME)
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
        form = context["form"]
        category_field = form.fields["category"]
        category_field.initial = settings.default_expenditures_category

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

        context["category_choices"] = json.dumps(grouped_categories)

        account_field = form.fields["account"]
        account_field.initial = settings.default_account

        return context


class TransactionCreateView(
    BaseTransactionFormViewMixin, mixins.LoginRequiredMixin, generic.CreateView
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
        return super().get_queryset().select_related("category", "account")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_form"] = forms.TransactionCreateForm(user=self.request.user)
        return context


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
            description=description,
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
        accounts = account_models.Account.objects.active().filter(
            owner=self.request.user
        )
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
