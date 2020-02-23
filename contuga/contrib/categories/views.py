from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy

from rest_framework import viewsets, permissions

from contuga.mixins import OnlyAuthoredByCurrentUserMixin
from . import models, serializers


class CategoryCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Category
    fields = ("name", "description")

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class CategoryListView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.ListView
):
    model = models.Category
    paginate_by = 20


class CategoryDetailView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Category


class CategoryUpdateView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.UpdateView
):
    model = models.Category
    fields = ("name", "description")
    template_name = "categories/category_update_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class CategoryDeleteView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DeleteView
):
    model = models.Category
    success_url = reverse_lazy("categories:list")


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CategorySerializer
    http_method_names = ("get", "post", "put", "patch", "delete")

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def get_queryset(self):
        return models.Category.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
