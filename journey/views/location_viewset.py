from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from journey.models.location import Location
from journey.serializers.location_serializer import LocationSerializer


class LocationViewSet(viewsets.ModelViewSet):
    """Joylashuvlar uchun to‘liq CRUD API."""
    queryset = Location.objects.all().order_by("-id")
    serializer_class = LocationSerializer

    # 🔹 Qo‘shimcha filtr: faqat O‘zbekistondagi joylar
    @action(detail=False, methods=["get"])
    def available(self, request):
        """Faqat O‘zbekiston hududidagi joylarni qaytaradi."""
        queryset = self.queryset.filter(is_available=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 🔹 Qo‘shimcha endpoint: koordinata bo‘yicha joy qo‘shish
    @action(detail=False, methods=["post"])
    def create_from_coords(self, request):
        """
        address, lat, lng orqali joy yaratish:
        {
            "address": "Tashkent City",
            "lat": 41.3111,
            "lng": 69.2797
        }
        """
        address = request.data.get("address")
        lat = request.data.get("lat")
        lng = request.data.get("lng")

        if not all([address, lat, lng]):
            return Response(
                {"detail": "address, lat va lng maydonlari kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        location = Location.create_loc(address, lat, lng)
        serializer = self.get_serializer(location)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
