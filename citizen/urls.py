from django.urls import path, include
from .views import *
from rest_framework import routers
app_name = 'citizen'

opinion_router = routers.SimpleRouter(trailing_slash=False)
opinion_router.register('citizen/opinion', OpinionViewSet, basename="opinion")

program_router = routers.SimpleRouter(trailing_slash=False)
program_router.register('citizen/program', ProgramViewSet, basename="program")

urlpatterns = [
    path('', include(opinion_router.urls)),
    path('', include(program_router.urls))
]