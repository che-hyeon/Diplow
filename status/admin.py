from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Nation)
admin.site.register(LocalGoverment)
admin.site.register(NationDashboard)
admin.site.register(LocalDashboard)
admin.site.register(ExchangeData)