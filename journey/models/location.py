from django.db import models
from geopy.geocoders import Nominatim
from functools import lru_cache


class Location(models.Model):
    name = models.CharField(max_length=100)
    coordinate = models.JSONField(default=dict, unique=True)  # {"lat": float, "lng": float}
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Joylashuv"
        verbose_name_plural = "Joylashuvlar"

    # =========================================================
    # 🔹 Caching bilan geografik tekshiruv
    # =========================================================
    @staticmethod
    @lru_cache(maxsize=1000)
    def _is_in_uzbekistan_cached(lat, lng):
        """Nominatim orqali joylashuvni bir marta tekshiradi va cache qiladi."""
        geolocator = Nominatim(user_agent="uzbekistan_validator_cache")
        try:
            location = geolocator.reverse((lat, lng), language="en")
            if location and "address" in location.raw:
                country_code = location.raw["address"].get("country_code", "").upper()
                return country_code == "UZ"
        except Exception:
            pass
        return False

    def clean(self):
        """O‘zbekiston hududida joylashganligini aniqlaydi (xato chiqarmaydi)."""
        lat = self.coordinate.get("lat")
        lng = self.coordinate.get("lng")

        if lat is None or lng is None:
            self.is_available = False
            return

        self.is_available = self._is_in_uzbekistan_cached(lat, lng)

    def save(self, *args, **kwargs):
        """Joylashuvni O‘zbekiston ichida yoki tashqarisida saqlaydi."""
        lat = self.coordinate.get("lat")
        lng = self.coordinate.get("lng")

        # Cache orqali tekshiruv
        self.is_available = self._is_in_uzbekistan_cached(lat, lng) if lat and lng else False

        super().save(*args, **kwargs)

    @classmethod
    def create_loc(cls, address, latitude, longitude):
        print(f"Creating location: {address}")
        return cls.objects.create(
            name=address,
            coordinate={"lat": latitude, "lng": longitude},
        )

    def __str__(self):
        lat = self.coordinate.get("lat")
        lng = self.coordinate.get("lng")
        return f"{self.name} ({lat}, {lng})"