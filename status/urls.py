from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'status'

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register('nation-status', NationDashViewSet, basename='nation')

local_router = routers.SimpleRouter(trailing_slash=False)
local_router.register('local-status', LocalDashViewSet, basename='local')

urlpatterns = [
    path('', include(default_router.urls)),
    path('', include(local_router.urls))
]