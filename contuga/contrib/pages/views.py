from django.urls import reverse
from django.views.generic.base import RedirectView, TemplateView

from . import constants, models


class PageRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse("transactions:list")
        else:
            return reverse("pages:home")


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Optimize section fetch with prefetch_related or select_related
        context["page"] = (
            models.Page.objects.prefetch_related("sections")
            .filter(type=constants.HOME_TYPE)
            .first()
        )
        return context
