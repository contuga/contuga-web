from django.contrib import admin

from . import models


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_filter = ('currency',
                   'created_at',
                   'updated_at')
    list_display = ('name',
                    'currency',
                    'balance',
                    'owner',
                    'created_at',
                    'updated_at')
    search_fields = ('name',
                     'balance')
    list_per_page = 15
