from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from journey.models import Travel, TravelInfo, TravelStatus, Location, Driver, Passenger


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'lat', 'lng']


class DriverSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name', 'contact', 'rating']


class PassengerSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['telegram_id', 'name', 'contact']


class TravelBaseSerializer(serializers.ModelSerializer):
    from_location = LocationSerializer(read_only=True)
    to_location = LocationSerializer(read_only=True)
    driver = DriverSimpleSerializer(read_only=True)

    class Meta:
        model = Travel
        fields = [
            'id', 'from_location', 'to_location', 'creator', 'driver',
            'expected_price', 'final_price', 'distance_km', 'estimated_duration_min',
            'started_at', 'completed_at', 'created_at'
        ]


class TravelCreateSerializer(serializers.ModelSerializer):
    from_location_id = serializers.IntegerField(write_only=True)
    to_location_id = serializers.IntegerField(write_only=True)
    creator = serializers.IntegerField()

    class Meta:
        model = Travel
        fields = [
            'from_location_id', 'to_location_id', 'creator',
            'expected_price', 'distance_km', 'estimated_duration_min'
        ]


class TravelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = [
            'expected_price', 'final_price', 'distance_km',
            'estimated_duration_min', 'started_at', 'completed_at'
        ]


class TravelDetailSerializer(TravelBaseSerializer):
    duration_minutes = serializers.ReadOnlyField()

    class Meta(TravelBaseSerializer.Meta):
        fields = TravelBaseSerializer.Meta.fields + ['duration_minutes']


class TravelInfoSerializer(serializers.ModelSerializer):
    passengers = PassengerSimpleSerializer(many=True, read_only=True)
    passenger_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = TravelInfo
        fields = [
            'id', 'has_female', 'status', 'special_requests',
            'driver_rating', 'passenger_rating', 'passengers', 'passenger_ids',
            'created_at', 'updated_at'
        ]


class TravelWithInfoSerializer(TravelDetailSerializer):
    info = TravelInfoSerializer(read_only=True)

    class Meta(TravelDetailSerializer.Meta):
        fields = TravelDetailSerializer.Meta.fields + ['info']


class TravelStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=TravelStatus.choices)


class TravelDriverUpdateSerializer(serializers.Serializer):
    driver_id = serializers.IntegerField()


class TravelRatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    rated_by = serializers.ChoiceField(choices=['driver', 'passenger'])


class TravelStatsSerializer(serializers.Serializer):
    total_travels = serializers.IntegerField()
    completed_travels = serializers.IntegerField()
    cancelled_travels = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)