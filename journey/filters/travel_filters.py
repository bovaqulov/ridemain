import django_filters
from django.db.models import Q
from journey.models import Travel, TravelInfo, TravelStatus


class TravelFilter(django_filters.FilterSet):
    creator = django_filters.NumberFilter(field_name='creator')
    driver = django_filters.NumberFilter(field_name='driver_id')
    status = django_filters.ChoiceFilter(field_name='info__status', choices=TravelStatus.choices)

    from_location = django_filters.NumberFilter(field_name='from_location_id')
    to_location = django_filters.NumberFilter(field_name='to_location_id')

    min_price = django_filters.NumberFilter(field_name='expected_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='expected_price', lookup_expr='lte')

    min_distance = django_filters.NumberFilter(field_name='distance_km', lookup_expr='gte')
    max_distance = django_filters.NumberFilter(field_name='distance_km', lookup_expr='lte')

    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    started_after = django_filters.DateTimeFilter(field_name='started_at', lookup_expr='gte')
    started_before = django_filters.DateTimeFilter(field_name='started_at', lookup_expr='lte')

    has_female = django_filters.BooleanFilter(field_name='info__has_female')

    search = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(from_location__name__icontains=value) |
            Q(to_location__name__icontains=value) |
            Q(driver__name__icontains=value)
        )

    class Meta:
        model = Travel
        fields = {
            'creator': ['exact'],
            'driver': ['exact'],
        }


class TravelInfoFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=TravelStatus.choices)
    has_female = django_filters.BooleanFilter()

    class Meta:
        model = TravelInfo
        fields = ['status', 'has_female']