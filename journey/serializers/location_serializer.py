# serializers.py
from rest_framework import serializers
from ..models.location import Location, UserLocation


class CoordinateSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=True)
    lng = serializers.FloatField(required=True)


class LocationSerializer(serializers.ModelSerializer):
    coordinate = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'lat', 'lng', 'coordinate', 'is_available', 'created_at']

    def get_coordinate(self, obj):
        return {"lat": obj.lat, "lng": obj.lng}


class UserLocationCreateSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField(required=True)
    coordinate = CoordinateSerializer(required=True)
    name = serializers.CharField(required=True)
    accuracy = serializers.FloatField(required=False, allow_null=True)
    live_period = serializers.IntegerField(required=False, allow_null=True)
    heading = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=360
    )


class UserLocationSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)

    class Meta:
        model = UserLocation
        fields = ['id', 'user', 'location', 'accuracy', 'live_period', 'heading', 'created_at']