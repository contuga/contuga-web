from django.views.generic.base import TemplateView
from django.shortcuts import redirect

from . import models, constants


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["page"] = (
            models.Page.objects.prefetch_related("sections")
            .filter(type=constants.HOME_TYPE)
            .first()
        )

        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("transactions:list")
        return super().dispatch(request, *args, **kwargs)
