from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy

from . import models


class TransactionCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Transaction
    fields = ('kind', 'amount', 'category', 'description')

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class TransactionListView(mixins.LoginRequiredMixin, generic.ListView):
    model = models.Transaction


class TransactionDetailView(mixins.LoginRequiredMixin, generic.DetailView):
    model = models.Transaction


class TransactionUpdateView(mixins.LoginRequiredMixin, generic.UpdateView):
    model = models.Transaction
    fields = ('kind', 'amount', 'category', 'description')

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class TransactionDeleteView(mixins.LoginRequiredMixin, generic.DeleteView):
    model = models.Transaction
    success_url = reverse_lazy('transactions:list')

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)
