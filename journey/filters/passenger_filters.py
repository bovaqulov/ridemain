import django_filters
from django.db.models import Q
from journey.models import Passenger


class PassengerFilter(django_filters.FilterSet):
    telegram_id = django_filters.NumberFilter(field_name='telegram_id')
    telegram_id__in = django_filters.BaseInFilter(field_name='telegram_id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    contact = django_filters.CharFilter(field_name='contact', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    min_trips = django_filters.NumberFilter(field_name='total_trips', lookup_expr='gte')
    max_trips = django_filters.NumberFilter(field_name='total_trips', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    search = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        """Umumiy qidiruv"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(contact__icontains=value) |
            Q(telegram_id__icontains=value)
        )

    class Meta:
        model = Passenger
        fields = {
            'telegram_id': ['exact'],
            'name': ['exact', 'icontains'],
            'contact': ['exact', 'icontains'],
        }


class PassengerBulkUpdateFilter(django_filters.FilterSet):
    """Bir nechta yo'lovchini yangilash uchun filter"""
    ids = django_filters.BaseInFilter(field_name='id', required=True)
    telegram_ids = django_filters.BaseInFilter(field_name='telegram_id')

    class Meta:
        model = Passenger
        fields = ['ids', 'telegram_ids']