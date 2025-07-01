from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(MovementData)
class MovementDataAdmin(admin.ModelAdmin):

    list_display = ('movement_data_id', 'category', 'title_kr', 'pub_date')
    list_display_links = list_display

@admin.register(DiplomacyEvent)
class DiplomacyEventAdmin(admin.ModelAdmin):

    list_display = ('event_id', 'event_category', 'event_title')
    list_display_links = list_display