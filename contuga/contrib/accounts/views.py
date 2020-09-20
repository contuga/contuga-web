from django.contrib.auth import mixins
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from rest_framework import permissions, viewsets

from contuga import views
from contuga.mixins import OnlyOwnedByCurrentUserMixin

from . import filters, models, serializers


class AccountCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Account
    fields = ("name", "currency", "description")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self):
        form = super().get_form()

        currency_field = form.fields["currency"]
        currency_field.queryset = currency_field.queryset.filter(
            author=self.request.user
        )

        return form


class AccountListView(
    OnlyOwnedByCurrentUserMixin, mixins.LoginRequiredMixin, views.FilteredListView
):
    model = models.Account
    paginate_by = 20
    filterset_class = filters.AccountFilterSet

    def get_queryset(self):
        return super().get_queryset().select_related("currency")


class AccountDetailView(
    OnlyOwnedByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Account

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("transactions", "transactions__category")
        )


class AccountUpdateView(
    OnlyOwnedByCurrentUserMixin, mixins.LoginRequiredMixin, generic.UpdateView
):
    model = models.Account
    fields = ("name", "description", "is_active")
    template_name = "accounts/account_update_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class AccountDeleteView(
    OnlyOwnedByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DeleteView
):
    model = models.Account
    success_url = reverse_lazy("accounts:list")


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AccountSerializer
    http_method_names = ("get", "post", "put", "patch", "delete")

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def get_queryset(self):
        return models.Account.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
