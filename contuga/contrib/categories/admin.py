from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('name',
                   'author',
                   'created_at',
                   'updated_at')
    list_display = ('name',
                    'author',
                    'created_at',
                    'updated_at')
    list_per_page = 15
    search_fields = ('name', 'author')
