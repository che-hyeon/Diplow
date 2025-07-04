from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'main'

movement_router = routers.SimpleRouter(trailing_slash=False)
movement_router.register('movement', TendDataKRViewSet, basename="movement")

diplomacy_router = routers.SimpleRouter(trailing_slash=False)
diplomacy_router.register('diplomacy', DiplomacyEventViewSet, basename="diplomacy")

movement_data_api = MovementDataAPI.as_view({'post': 'load_movement_data'})

urlpatterns = [
    path('', include(movement_router.urls)),
    path('', include(diplomacy_router.urls)),

    path('load/movement/data', movement_data_api)
]