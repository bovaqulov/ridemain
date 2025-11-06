from django.core.validators import MaxValueValidator
from django.db import models
from .driver import Driver
from .location import Location
from .passengers import Passenger

class TravelStatus(models.TextChoices):
    CREATED = "created", "Yaratildi"
    SEARCHING_DRIVER = "searching_driver", "Haydovchi qidirilmoqda"
    DRIVER_FOUND = "driver_found", "Haydovchi topildi"
    ARRIVED = "arrived", "Yetib keldi"
    STARTED = "started", "Sayohat boshlandi"
    COMPLETED = "completed", "Yakunlandi"
    CANCELLED = "cancelled", "Bekor qilindi"
    FAILED = "failed", "Xatolik"

class Travel(models.Model):
    from_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="travels_from",
        verbose_name='Boshlanish joyi',
        null=True,
        blank=True
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="travels_to",
        verbose_name='Tugash joyi',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    creator = models.BigIntegerField(db_index=True, verbose_name='Yaratuvchi Telegram ID')
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        related_name="travels",
        verbose_name='Haydovchi',
        null=True,
        blank=True
    )
    expected_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Kutilayotgan narx'
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Yakuniy narx'
    )
    distance_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Masofa (km)'
    )
    estimated_duration_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Taxminiy davomiylik (min)'
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Boshlangan vaqt')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tugagan vaqt')

    class Meta:
        verbose_name = "Sayohat"
        verbose_name_plural = "Sayohatlar"
        indexes = [
            models.Index(fields=['creator', 'created_at']),
            models.Index(fields=['driver', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_location} ➔ {self.to_location}"

    @property
    def duration_minutes(self):
        """Sayohatning haqiqiy davomiyligi"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() // 60
        return None

class TravelInfo(models.Model):
    travel = models.OneToOneField(
        Travel,
        on_delete=models.CASCADE,
        related_name="info",
        verbose_name='Sayohat'
    )
    passengers = models.ManyToManyField(
        Passenger,
        related_name='travels',
        verbose_name='Yoʻlovchilar',
        blank=True
    )
    has_female = models.BooleanField(default=False, verbose_name='Ayol yoʻlovchi bor')
    status = models.CharField(
        max_length=20,
        choices=TravelStatus.choices,
        default=TravelStatus.CREATED,
        verbose_name='Holati'
    )
    special_requests = models.TextField(blank=True, verbose_name='Maxsus soʻrovlar')
    driver_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(5)],
        verbose_name='Haydovchi reytingi'
    )
    passenger_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(5)],
        verbose_name='Yoʻlovchi reytingi'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sayohat ma'lumoti"
        verbose_name_plural = "Sayohat ma'lumotlari"

    def __str__(self):
        return f"Travel Info for {self.travel}"