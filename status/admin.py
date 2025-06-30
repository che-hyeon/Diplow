from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Nation)
admin.site.register(LocalGoverment)
admin.site.register(NationDashboard)
admin.site.register(LocalDashboard)
admin.site.register(Vision)

@admin.register(ExchangeData)
class ExchangeDataAdmin(admin.ModelAdmin):

    list_display = ('exchange_id', 'exchange_name_kr', 'exchange_nation', 'exchange_category')
    list_display_links = list_display
    search_fields = ('exchange_name_kr',)

@admin.register(LocalData)
class LocalDataAdmin(admin.ModelAdmin):

    list_display = ('local_data_id', 'origin_city', 'partner_city', 'category')
    list_display_links = list_display

@admin.register(ExchangeCategory)
class ExchangeCategoryAdmin(admin.ModelAdmin):

    list_display = ('exchange_category_id', 'local', 'exchange_name', 'exchange_num')
    list_display_links = list_display