from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .location import Location

class CarType(models.TextChoices):
    ECONOMY = 'economy', 'Economy'
    STANDARD = 'standard', 'Standard'
    BUSINESS = 'business', 'Business'

class Car(models.Model):
    name = models.CharField(max_length=100, verbose_name='Mashina nomi')
    model = models.CharField(max_length=100, verbose_name='Model')
    car_type = models.CharField(
        max_length=20,
        choices=CarType.choices,
        default=CarType.STANDARD,
        verbose_name='Mashina turi'
    )
    color = models.CharField(max_length=50, blank=True, verbose_name='Rangi')
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1990), MaxValueValidator(2030)],
        null=True,
        blank=True,
        verbose_name='Ishlab chiqarilgan yili'
    )
    license_plate = models.CharField(max_length=20, unique=True, verbose_name='Davlat raqami')
    capacity = models.PositiveIntegerField(default=4, verbose_name='Oʻrindiqlar soni')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mashina'
        verbose_name_plural = 'Mashinalar'
        indexes = [
            models.Index(fields=['license_plate']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} {self.model} ({self.license_plate})"

class DriverStatus(models.TextChoices):
    ACTIVE = 'active', 'Faol'
    INACTIVE = 'inactive', 'Faol emas'
    BUSY = 'busy', 'Band'
    OFFLINE = 'offline', 'Offline'

class Driver(models.Model):
    telegram_id = models.BigIntegerField(db_index=True, unique=True, verbose_name='Telegram ID')
    name = models.CharField(max_length=100, verbose_name='Ism')
    contact = models.CharField(max_length=20, db_index=True, verbose_name='Telefon raqam')
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers',
        verbose_name='Mashina'
    )
    status = models.CharField(
        max_length=20,
        choices=DriverStatus.choices,
        default=DriverStatus.INACTIVE,
        verbose_name='Holati'
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Reyting'
    )
    total_trips = models.PositiveIntegerField(default=0, verbose_name='Jami sayohatlar')
    is_verified = models.BooleanField(default=False, verbose_name='Tasdiqlangan')
    current_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers_current',
        verbose_name='Joriy joylashuv'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Haydovchi'
        verbose_name_plural = 'Haydovchilar'
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['status']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.name} ({self.contact})"

class DriverRoad(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='roads',
        verbose_name='Haydovchi'
    )
    from_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='road_starts',
        verbose_name='Boshlanish joyi'
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='road_ends',
        verbose_name='Tugash joyi'
    )
    current_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='road_current',
        verbose_name='Joriy joylashuv'
    )
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Haydovchi yoʻli'
        verbose_name_plural = 'Haydovchi yoʻllari'
        indexes = [
            models.Index(fields=['driver', 'is_active']),
            models.Index(fields=['from_location', 'to_location']),
        ]

    def __str__(self):
        return f"{self.driver.name}: {self.from_location} → {self.to_location}"