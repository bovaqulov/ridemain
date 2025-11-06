# admin.py
from django.contrib import admin
from .models import *


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "lat_display", "lng_display", "is_available", "created_at", "updated_at")
    list_filter = ("is_available", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("name", "lat", "lng", "is_available")
        }),
        ("Tizim ma'lumotlari", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.display(description="Latitude")
    def lat_display(self, obj):
        return f"{obj.lat:.6f}"

    @admin.display(description="Longitude")
    def lng_display(self, obj):
        return f"{obj.lng:.6f}"


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "location",
        "accuracy_display",
        "live_period_display",
        "heading_display",
        "created_at",
    )
    list_filter = ("created_at", "location__is_available")
    search_fields = ("user", "location__name")
    autocomplete_fields = ("location",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Foydalanuvchi ma'lumotlari", {
            "fields": ("user", "location")
        }),
        ("Qo‘shimcha ma’lumotlar", {
            "fields": ("accuracy", "live_period", "heading")
        }),
        ("Tizim ma'lumotlari", {
            "fields": ("created_at",),
        }),
    )

    @admin.display(description="Aniqlik (m)")
    def accuracy_display(self, obj):
        return f"{obj.accuracy:.1f}" if obj.accuracy is not None else "-"

    @admin.display(description="Live period (s)")
    def live_period_display(self, obj):
        return f"{obj.live_period}s" if obj.live_period else "-"

    @admin.display(description="Yo‘nalish (°)")
    def heading_display(self, obj):
        return f"{obj.heading}°" if obj.heading is not None else "-"


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'car_type', 'license_plate', 'capacity', 'is_active']
    list_filter = ['car_type', 'is_active', 'year']
    search_fields = ['name', 'model', 'license_plate']
    list_editable = ['is_active']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'telegram_id', 'contact', 'car', 'status', 'rating', 'is_verified']
    list_filter = ['status', 'is_verified', 'created_at']
    search_fields = ['name', 'contact', 'telegram_id']
    list_editable = ['status', 'is_verified']


@admin.register(DriverRoad)
class DriverRoadAdmin(admin.ModelAdmin):
    list_display = ['driver', 'from_location', 'to_location', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['driver__name', 'from_location__name', 'to_location__name']


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['name', 'telegram_id', 'contact', 'rating', 'total_trips', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact', 'telegram_id']
    list_editable = ['is_active']


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = ['from_location', 'to_location', 'creator', 'driver', 'created_at', 'status']
    list_filter = ['created_at', 'started_at', 'completed_at']
    search_fields = ['creator', 'driver__name', 'from_location__name', 'to_location__name']

    def status(self, obj):
        return obj.info.status if hasattr(obj, 'info') else 'Noma\'lum'

    status.short_description = 'Holati'

@admin.register(TravelInfo)
class TravelInfoAdmin(admin.ModelAdmin):
    list_display = ['travel', 'status', 'has_female', 'created_at']
    list_filter = ['status', 'has_female', 'created_at']
    search_fields = ['travel__from_location__name', 'travel__to_location__name']
    filter_horizontal = ['passengers']
