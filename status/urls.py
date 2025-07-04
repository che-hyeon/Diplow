from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'status'

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register('nation-status', NationDashViewSet, basename='nation')

local_router = routers.SimpleRouter(trailing_slash=False)
local_router.register('local-status', LocalDashViewSet, basename='local')

exchange_api_3 = ExchangeDataAPI.as_view({'post': 'load_public_data_3'})
exchange_api_4 = ExchangeDataAPI.as_view({'post': 'load_public_data_4'})
exchange_api_1 = ExchangeDataAPI.as_view({'post': 'load_public_data_1'})

seoul_sister_api = LocalDataAPI.as_view({'post': 'load_seoul_sister_data'})
seoul_friendly_api = LocalDataAPI.as_view({'post': 'load_seoul_friendly_data'})

pusan_sister_api = LocalDataAPI.as_view({'post': 'load_pusan_sister_data'})
pusan_friendly_api = LocalDataAPI.as_view({'post': 'load_pusan_friendly_data'})

incheon_sister_api = LocalDataAPI.as_view({'post': 'load_incheon_sister_data'})

jeju_local_api = LocalDataAPI.as_view({'post': 'load_jeju_local_data'})

urlpatterns = [
    path('', include(default_router.urls)),
    path('', include(local_router.urls)),

    path('status/exchange/load-3', exchange_api_3),
    path('status/exchange/load-4', exchange_api_4),
    path('status/exchange/load-1', exchange_api_1),

    path('status/local/seoul/sister', seoul_sister_api),
    path('status/local/seoul/friendly', seoul_friendly_api),

    path('status/local/pusan/sister', pusan_sister_api),
    path('status/local/pusan/friendly', pusan_friendly_api),

    path('status/local/incheon/sister', incheon_sister_api),

    path('status/local/jeju', jeju_local_api),

]