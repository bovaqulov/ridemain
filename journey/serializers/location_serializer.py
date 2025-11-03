from rest_framework import serializers
from journey.models.location import Location


class LocationSerializer(serializers.ModelSerializer):
    """Location model uchun serializer."""

    class Meta:
        model = Location
        fields = ["id", "name", "coordinate", "is_available"]
        read_only_fields = ["is_available"]

    def validate_coordinate(self, value):
        """Koordinata formati to‘g‘riligini tekshiradi."""
        if not isinstance(value, dict) or "lat" not in value or "lng" not in value:
            raise serializers.ValidationError(
                "Koordinata formati noto‘g‘ri. {'lat': float, 'lng': float} ko‘rinishida bo‘lishi kerak."
            )
        try:
            float(value["lat"])
            float(value["lng"])
        except (TypeError, ValueError):
            raise serializers.ValidationError("Lat va Lng qiymatlari raqam bo‘lishi kerak.")
        return value
