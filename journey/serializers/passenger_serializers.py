from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from journey.models import Passenger


class PassengerBaseSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(
        min_value=1,
        help_text="Telegram user ID"
    )
    name = serializers.CharField(
        max_length=100,
        help_text="Yo'lovchi ismi"
    )
    contact = serializers.CharField(
        max_length=20,
        help_text="Telefon raqami"
    )

    class Meta:
        model = Passenger
        fields = ['telegram_id', 'name', 'contact']


class PassengerCreateSerializer(PassengerBaseSerializer):
    def validate_telegram_id(self, value):
        if Passenger.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError(
                "Bu Telegram ID bilan foydalanuvchi allaqachon mavjud"
            )
        return value


class PassengerUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=False)
    contact = serializers.CharField(max_length=20, required=False)

    class Meta:
        model = Passenger
        fields = ['name', 'contact', 'is_active']


class PassengerDetailSerializer(PassengerBaseSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    total_trips = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta(PassengerBaseSerializer.Meta):
        fields = PassengerBaseSerializer.Meta.fields + [
            'rating', 'total_trips', 'is_active',
            'created_at', 'updated_at'
        ]


class PassengerListSerializer(PassengerBaseSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    total_trips = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta(PassengerBaseSerializer.Meta):
        fields = PassengerBaseSerializer.Meta.fields + [
            'rating', 'total_trips', 'is_active'
        ]


class PassengerRatingSerializer(serializers.Serializer):
    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )


class PassengerStatsSerializer(serializers.Serializer):
    total_passengers = serializers.IntegerField()
    active_passengers = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_trips = serializers.IntegerField()