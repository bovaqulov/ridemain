from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError, NotFound
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Count, Avg, Sum, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from journey.models import Travel, TravelInfo, TravelStatus, Location, Driver, Passenger
from journey.serializers.travel_serializers import (
    TravelCreateSerializer,
    TravelUpdateSerializer,
    TravelDetailSerializer,
    TravelWithInfoSerializer,
    TravelStatusUpdateSerializer,
    TravelDriverUpdateSerializer,
    TravelRatingSerializer,
    TravelStatsSerializer
)
from journey.filters.travel_filters import TravelFilter


class TravelViewSet(viewsets.ModelViewSet):
    """
    Sayohatlar uchun CRUD operatsiyalari
    """

    queryset = Travel.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TravelFilter
    search_fields = ['from_location__name', 'to_location__name', 'driver__name']
    ordering_fields = [
        'created_at', 'started_at', 'completed_at',
        'expected_price', 'distance_km'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        action_serializers = {
            'create': TravelCreateSerializer,
            'update': TravelUpdateSerializer,
            'partial_update': TravelUpdateSerializer,
            'retrieve': TravelWithInfoSerializer,
            'list': TravelDetailSerializer,
        }
        return action_serializers.get(self.action, TravelDetailSerializer)

    def get_queryset(self):
        """Querysetni optimize qilish"""
        return Travel.objects.select_related(
            'from_location', 'to_location', 'driver'
        ).prefetch_related('info__passengers')

    def create(self, request, *args, **kwargs):
        """Yangi sayohat yaratish"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                # Locationlarni tekshirish
                from_location = get_object_or_404(
                    Location,
                    id=serializer.validated_data['from_location_id']
                )
                to_location = get_object_or_404(
                    Location,
                    id=serializer.validated_data['to_location_id']
                )

                travel = Travel.objects.create(
                    from_location=from_location,
                    to_location=to_location,
                    creator=serializer.validated_data['creator'],
                    expected_price=serializer.validated_data.get('expected_price'),
                    distance_km=serializer.validated_data.get('distance_km'),
                    estimated_duration_min=serializer.validated_data.get('estimated_duration_min')
                )

                # TravelInfo yaratish
                TravelInfo.objects.create(travel=travel)

        except Exception as e:
            return Response(
                {'error': f'Sayohat yaratishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            TravelWithInfoSerializer(travel).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Sayohat ma'lumotlarini yangilash"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_update(serializer)
        except Exception as e:
            return Response(
                {'error': f'Yangilashda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(TravelWithInfoSerializer(instance).data)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Sayohat statusini yangilash"""
        travel = self.get_object()
        serializer = TravelStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']

        try:
            with transaction.atomic():
                travel.info.status = new_status

                # Statusga qarab vaqtlarni yangilash
                if new_status == TravelStatus.STARTED and not travel.started_at:
                    travel.started_at = timezone.now()
                elif new_status == TravelStatus.COMPLETED and not travel.completed_at:
                    travel.completed_at = timezone.now()

                travel.info.save()
                travel.save()

        except Exception as e:
            return Response(
                {'error': f'Status yangilashda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(TravelWithInfoSerializer(travel).data)

    @action(detail=True, methods=['post'], url_path='assign-driver')
    def assign_driver(self, request, pk=None):
        """Haydovchi tayinlash"""
        travel = self.get_object()
        serializer = TravelDriverUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        driver_id = serializer.validated_data['driver_id']

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            raise NotFound({'error': 'Haydovchi topilmadi'})

        try:
            with transaction.atomic():
                travel.driver = driver
                travel.save()

        except Exception as e:
            return Response(
                {'error': f'Haydovchi tayinlashda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(TravelWithInfoSerializer(travel).data)

    @action(detail=True, methods=['post'], url_path='add-passengers')
    def add_passengers(self, request, pk=None):
        """Yo'lovchi qo'shish"""
        travel = self.get_object()
        passenger_ids = request.data.get('passenger_ids', [])

        if not passenger_ids:
            return Response(
                {'error': 'passenger_ids maydoni talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            passengers = Passenger.objects.filter(telegram_id__in=passenger_ids)

            with transaction.atomic():
                travel.info.passengers.add(*passengers)

                # Agar ayol yo'lovchi bo'lsa, has_female ni True qilish
                if not travel.info.has_female:
                    female_passengers = passengers.filter(
                        Q(name__icontains='a') | Q(name__icontains='o')  # Soddalashtirilgan tekshiruv
                    )
                    if female_passengers.exists():
                        travel.info.has_female = True
                        travel.info.save()

        except Exception as e:
            return Response(
                {'error': f'Yo\'lovchi qo\'shishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(TravelWithInfoSerializer(travel).data)

    @action(detail=True, methods=['post'], url_path='rate')
    def rate_travel(self, request, pk=None):
        """Sayohatni baholash"""
        travel = self.get_object()
        serializer = TravelRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating = serializer.validated_data['rating']
        rated_by = serializer.validated_data['rated_by']

        try:
            with transaction.atomic():
                if rated_by == 'driver':
                    travel.info.passenger_rating = rating
                else:  # passenger
                    travel.info.driver_rating = rating

                travel.info.save()

        except Exception as e:
            return Response(
                {'error': f'Baholashda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(TravelWithInfoSerializer(travel).data)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_travel(self, request, pk=None):
        """Sayohatni yakunlash"""
        travel = self.get_object()
        final_price = request.data.get('final_price')

        try:
            with transaction.atomic():
                travel.info.status = TravelStatus.COMPLETED
                travel.completed_at = timezone.now()

                if final_price:
                    travel.final_price = final_price

                travel.info.save()
                travel.save()

        except Exception as e:
            return Response(
                {'error': f'Yakunlashda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(TravelWithInfoSerializer(travel).data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_travel(self, request, pk=None):
        """Sayohatni bekor qilish"""
        travel = self.get_object()

        try:
            with transaction.atomic():
                travel.info.status = TravelStatus.CANCELLED
                travel.info.save()

        except Exception as e:
            return Response(
                {'error': f'Bekor qilishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(TravelWithInfoSerializer(travel).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Sayohatlar statistikasi"""
        stats = Travel.objects.aggregate(
            total_travels=Count('id'),
            completed_travels=Count('id', filter=Q(info__status=TravelStatus.COMPLETED)),
            cancelled_travels=Count('id', filter=Q(info__status=TravelStatus.CANCELLED)),
            total_revenue=Sum('final_price'),
            average_rating=Avg('info__driver_rating')
        )

        serializer = TravelStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-creator')
    def by_creator(self, request):
        """Yaratuvchi bo'yicha sayohatlar"""
        creator_id = request.query_params.get('creator_id')

        if not creator_id:
            raise ValidationError({'error': 'creator_id parametri talab qilinadi'})

        travels = self.filter_queryset(
            self.get_queryset().filter(creator=creator_id)
        )

        page = self.paginate_queryset(travels)
        if page is not None:
            serializer = TravelDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TravelDetailSerializer(travels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-driver')
    def by_driver(self, request):
        """Haydovchi bo'yicha sayohatlar"""
        driver_id = request.query_params.get('driver_id')

        if not driver_id:
            raise ValidationError({'error': 'driver_id parametri talab qilinadi'})

        travels = self.filter_queryset(
            self.get_queryset().filter(driver_id=driver_id)
        )

        page = self.paginate_queryset(travels)
        if page is not None:
            serializer = TravelDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TravelDetailSerializer(travels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='active')
    def active_travels(self, request):
        """Faol sayohatlar"""
        active_statuses = [
            TravelStatus.CREATED,
            TravelStatus.SEARCHING_DRIVER,
            TravelStatus.DRIVER_FOUND,
            TravelStatus.ARRIVED,
            TravelStatus.STARTED
        ]

        active_travels = self.filter_queryset(
            self.get_queryset().filter(info__status__in=active_statuses)
        )

        page = self.paginate_queryset(active_travels)
        if page is not None:
            serializer = TravelDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TravelDetailSerializer(active_travels, many=True)
        return Response(serializer.data)