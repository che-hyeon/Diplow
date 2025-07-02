from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'status'

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register('nation-status', NationDashViewSet, basename='nation')

local_router = routers.SimpleRouter(trailing_slash=False)
local_router.register('local-status', LocalDashViewSet, basename='local')

exchange_api = ExchangeDataAPI.as_view({'post': 'load_public_data_3'})

urlpatterns = [
    path('', include(default_router.urls)),
    path('', include(local_router.urls)),

    path('status/exchange/load', exchange_api)
]