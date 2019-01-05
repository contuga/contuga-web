from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy

from . import models


class CategoryCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Category
    fields = ('name', 'description')

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class CategoryListView(mixins.LoginRequiredMixin, generic.ListView):
    model = models.Category
    paginate_by = 10


class CategoryDetailView(mixins.LoginRequiredMixin, generic.DetailView):
    model = models.Category


class CategoryUpdateView(mixins.LoginRequiredMixin, generic.UpdateView):
    model = models.Category
    fields = ('name', 'description')

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class CategoryDeleteView(mixins.LoginRequiredMixin, generic.DeleteView):
    model = models.Category
    success_url = reverse_lazy('categories:list')

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)
