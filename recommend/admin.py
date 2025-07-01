from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(EnvironIssueData)
class EnvironIssueDataAdmin(admin.ModelAdmin):

    list_display = ('environ_data_id', 'nation', 'environ_data_title', 'pub_date')
    list_display_links = list_display