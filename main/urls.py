from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'main'

movement_router = routers.SimpleRouter(trailing_slash=False)
movement_router.register('movement', TendDataKRViewSet, basename="movement")

diplomacy_router = routers.SimpleRouter(trailing_slash=False)
diplomacy_router.register('diplomacy', DiplomacyEventViewSet, basename="diplomacy")

urlpatterns = [
    path('', include(movement_router.urls)),
    path('', include(diplomacy_router.urls))
]