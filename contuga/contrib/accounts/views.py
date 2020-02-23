from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy

from contuga.mixins import OnlyOwnedByCurrentUserMixin
from . import models


class AccountCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Account
    fields = ("name", "currency", "description")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class AccountListView(
    OnlyOwnedByCurrentUserMixin, mixins.LoginRequiredMixin, generic.ListView
):
    model = models.Account
    paginate_by = 10


class AccountDetailView(
    OnlyOwnedByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Account


class AccountUpdateView(
    OnlyOwnedByCurrentUserMixin, mixins.LoginRequiredMixin, generic.UpdateView
):
    model = models.Account
    fields = ("name", "description")
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
