# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Joylashuv"
        verbose_name_plural = "Joylashuvlar"
        unique_together = ['lat', 'lng']  # Bir xil koordinatali locationlar qayta yaratilmasligi uchun
        indexes = [
            models.Index(fields=['lat', 'lng']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f"{self.name} ({self.lat:.6f}, {self.lng:.6f})"

    @property
    def coordinate(self):
        """Coordinate ni JSON formatida qaytarish"""
        return {"lat": self.lat, "lng": self.lng}


class UserLocation(models.Model):
    user = models.BigIntegerField(db_index=True)  # Telegram ID
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='user_locations')
    created_at = models.DateTimeField(auto_now_add=True)

    # Qo'shimcha ma'lumotlar
    accuracy = models.FloatField(null=True, blank=True)  # Lokatsiya aniqligi
    live_period = models.IntegerField(null=True, blank=True)  # Live location period
    heading = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)]
    )  # Yo'nalish (0-360)

    class Meta:
        verbose_name = "Foydalanuvchi joylashuvi"
        verbose_name_plural = "Foydalanuvchi joylashuvlari"
        ordering = ['-created_at']
        unique_together = ['location']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"User {self.user} at {self.location.name}"