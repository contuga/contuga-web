from django.views import generic
from django.http import JsonResponse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext_lazy as _


class FilteredListView(generic.ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(
            self.request.GET, request=self.request, queryset=queryset
        )
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class ManifestView(generic.View):
    def get(self, request):
        manifest = {
            "name": "Contuga",
            "short_name": "Contuga",
            "description": _("Simple web-based expense manager"),
            "icons": [
                {
                    "src": static("icons/favicon-16x16.png"),
                    "type": "image/png",
                    "sizes": "16x16",
                },
                {
                    "src": static("icons/favicon-32x32.png"),
                    "type": "image/png",
                    "sizes": "32x32",
                },
                {
                    "src": static("icons/apple-touch-icon-57x57.png"),
                    "type": "image/png",
                    "sizes": "57x57",
                },
                {
                    "src": static("icons/apple-touch-icon-60x60.png"),
                    "type": "image/png",
                    "sizes": "72x72",
                },
                {
                    "src": static("icons/apple-touch-icon-76x76.png"),
                    "type": "image/png",
                    "sizes": "76x76",
                },
                {
                    "src": static("icons/apple-touch-icon-114x114.png"),
                    "type": "image/png",
                    "sizes": "114x114",
                },
                {
                    "src": static("icons/apple-touch-icon-120x120.png"),
                    "type": "image/png",
                    "sizes": "120x120",
                },
                {
                    "src": static("icons/apple-touch-icon-144x144.png"),
                    "type": "image/png",
                    "sizes": "144x144",
                },
                {
                    "src": static("icons/apple-touch-icon-152x152.png"),
                    "type": "image/png",
                    "sizes": "152x152",
                },
                {
                    "src": static("icons/apple-touch-icon-180x180.png"),
                    "type": "image/png",
                    "sizes": "180x180",
                },
                {
                    "src": static("icons/android-chrome-192x192.png"),
                    "type": "image/png",
                    "sizes": "192x192",
                },
                {
                    "src": static("icons/android-chrome-512x512.png"),
                    "type": "image/png",
                    "sizes": "512x512",
                },
            ],
            "background_color": "#ffffff",
            "theme_color": "#ffffff",
            "start_url": "/",
            "display": "standalone",
        }
        return JsonResponse(manifest)
