from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableStackedInline

from . import models


class PageSectionInline(admin.StackedInline, TranslatableStackedInline):
    model = models.PageSection
    extra = 0


@admin.register(models.Page)
class PageAdmin(TranslatableAdmin):
    list_filter = ("type", "created_at", "updated_at")
    list_display = ("title", "type", "created_at", "updated_at")
    list_per_page = 15
    search_fields = ("title",)
    inlines = [PageSectionInline]

    def get_prepopulated_fields(self, request, obj=None):
        # Can't use `prepopulated_fields` because it of the admin validation
        # for translated fields. This is the official django-parler workaround.
        return {"slug": ("title",)}
