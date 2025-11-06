from django.db import models

class Passenger(models.Model):
    telegram_id = models.BigIntegerField(db_index=True, unique=True, verbose_name='Telegram ID')
    name = models.CharField(max_length=100, verbose_name='Ism')
    contact = models.CharField(max_length=20, unique=True, verbose_name='Telefon raqam')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        verbose_name='Reyting'
    )
    total_trips = models.PositiveIntegerField(default=0, verbose_name='Jami sayohatlar')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Yoʻlovchi'
        verbose_name_plural = 'Yoʻlovchilar'
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.contact})"