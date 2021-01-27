from django.contrib.auth import mixins
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from rest_framework import permissions, viewsets

from contuga import views
from contuga.mixins import OnlyAuthoredByCurrentUserMixin

from . import filters, forms, models, serializers


class CategoryCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Category
    fields = ("name", "transaction_type", "description")

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class CategoryListView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, views.FilteredListView
):
    model = models.Category
    paginate_by = 20
    filterset_class = filters.CategoryFilterSet


class CategoryDetailView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Category

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "transactions",
                "transactions__income_counterpart",
                "transactions__account",
                "transactions__account__currency",
            )
        )


class CategoryUpdateView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.UpdateView
):
    model = models.Category
    form_class = forms.CategoryUpdateForm
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
