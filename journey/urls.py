from django.urls import path, include
from rest_framework.routers import DefaultRouter
from journey.views.location_viewset import LocationViewSet

router = DefaultRouter()
router.register(r"locations", LocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
]
