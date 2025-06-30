from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'status'

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register('status', NationDashViewSet, basename='status')

urlpatterns = [
    path('', include(default_router.urls))
]