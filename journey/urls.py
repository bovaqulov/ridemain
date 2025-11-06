# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.location_viewset import LocationViewSet
from .views.passenger_views import PassengerViewSet
from .views.travel_views import TravelViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'passengers', PassengerViewSet,basename='passenger')
router.register(r'travels', TravelViewSet, basename='travel')

urlpatterns = [

    path('journey/', include(router.urls)),
]