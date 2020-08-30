from django.contrib.auth import mixins
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from rest_framework import permissions, viewsets

from contuga import views
from contuga.mixins import OnlyAuthoredByCurrentUserMixin

from . import models, serializers


class CurrencyCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Currency
    fields = ("name",)

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class CurrencyListView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.ListView
):
    model = models.Currency
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset()


class CurrencyDetailView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Currency

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("transactions", "transactions__currency")
        )


class CurrencyUpdateView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.UpdateView
):
    model = models.Currency
    fields = ("name")
    template_name = "currencies/currency_update_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class CurrencyDeleteView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DeleteView
):
    model = models.Currency
    success_url = reverse_lazy("currencies:list")


class CurrencyViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CurrencySerializer
    http_method_names = ("get", "post", "put", "patch", "delete")

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def get_queryset(self):
        return models.Currency.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
