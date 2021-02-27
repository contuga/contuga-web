from django.contrib.auth import mixins
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django_filters import rest_framework
from rest_framework import permissions, viewsets

from contuga.mixins import OnlyAuthoredByCurrentUserMixin

from . import filters, models, serializers


class TagCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Tag
    fields = ("name",)

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class TagListView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.ListView
):
    model = models.Tag
    paginate_by = 20


class TagDetailView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DetailView
):
    model = models.Tag

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


class TagUpdateView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.UpdateView
):
    model = models.Tag
    fields = ("name",)
    template_name = "tags/tag_update_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class TagDeleteView(
    OnlyAuthoredByCurrentUserMixin, mixins.LoginRequiredMixin, generic.DeleteView
):
    model = models.Tag
    success_url = reverse_lazy("tags:list")


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TagSerializer
    http_method_names = ("get", "post", "put", "patch", "delete")
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = filters.TagFilterSet

    def get_permissions(self):
        permission_classes = super().get_permissions()
        permission_classes.append(permissions.IsAuthenticated())
        return permission_classes

    def get_queryset(self):
        return models.Tag.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
