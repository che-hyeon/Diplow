from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'recommend'

nation_info_router = routers.SimpleRouter(trailing_slash=False)
nation_info_router.register('recommend/nation-info', NationInfoViewSet, basename="nation_info")

environ_router = routers.SimpleRouter(trailing_slash=False)
environ_router.register('recommend/nation-environ', EnvironIssueDataViewSet, basename="nation_environ")

load_environ_data = EnvironIssueDataAPI.as_view({'post': 'load_environ_data'})

urlpatterns = [
    path('', include(nation_info_router.urls)),
    path('', include(environ_router.urls)),

    path('recommend/load-environ', load_environ_data)
]