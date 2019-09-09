from django.contrib import admin

from . import models


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_filter = ("author", "created_at", "updated_at")
    list_display = ("amount", "author", "created_at", "updated_at")
    list_per_page = 15
    search_fields = ("amount", "author")
