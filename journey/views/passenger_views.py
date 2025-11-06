from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import NotFound, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction, models
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404

from journey.models import Passenger
from journey.serializers.passenger_serializers import (
    PassengerCreateSerializer,
    PassengerUpdateSerializer,
    PassengerDetailSerializer,
    PassengerListSerializer,
    PassengerRatingSerializer,
    PassengerStatsSerializer
)
from journey.filters.passenger_filters import PassengerFilter


class PassengerViewSet(viewsets.ModelViewSet):
    """
    Telegram ID asosida yo'lovchilar uchun CRUD operatsiyalari
    """

    queryset = Passenger.objects.all()
    lookup_field = 'telegram_id'
    lookup_url_kwarg = 'telegram_id'

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PassengerFilter
    search_fields = ['name', 'contact', 'telegram_id']
    ordering_fields = ['name', 'rating', 'total_trips', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        action_serializers = {
            'create': PassengerCreateSerializer,
            'update': PassengerUpdateSerializer,
            'partial_update': PassengerUpdateSerializer,
            'retrieve': PassengerDetailSerializer,
            'list': PassengerListSerializer,
        }
        return action_serializers.get(self.action, PassengerDetailSerializer)

    def get_object(self, tg_id=None):
        """Telegram ID bo'yicha objectni olish"""
        telegram_id = self.kwargs.get('telegram_id')

        if not telegram_id:
            raise ValidationError({'error': 'telegram_id kiritilmagan'})
        try:
            return Passenger.objects.get(telegram_id=telegram_id)
        except Passenger.DoesNotExist:
            # Bu joyda siz istalgan javobni tashlashingiz mumkin
            raise NotFound({'status': False, 'error': 'Yo\'lovchi topilmadi'})
        except ValueError:
            raise ValidationError({'error': 'Noto\'g\'ri Telegram ID format'})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                passenger = serializer.save()
        except Exception as e:
            return Response(
                {'error': f'Yaratishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            PassengerDetailSerializer(passenger).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
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

        return Response(PassengerDetailSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            with transaction.atomic():
                self.perform_destroy(instance)
        except Exception as e:
            return Response(
                {'error': f'O\'chirishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': 'Yo\'lovchi muvaffaqiyatli o\'chirildi'},
            status=status.HTTP_204_NO_CONTENT
        )


    @action(detail=True, methods=['post'], url_path='update-rating')
    def update_rating(self, request, telegram_id=None):
        """Reyting yangilash"""
        passenger = self.get_object()
        serializer = PassengerRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                passenger.rating = serializer.validated_data['rating']
                passenger.save()
        except Exception as e:
            return Response(
                {'error': f'Reyting yangilashda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(PassengerDetailSerializer(passenger).data)

    @action(detail=True, methods=['post'], url_path='increment-trips')
    def increment_trips(self, request, telegram_id=None):
        """Sayohatlar sonini oshirish"""
        passenger = self.get_object()

        try:
            with transaction.atomic():
                passenger.total_trips += 1
                passenger.save()
        except Exception as e:
            return Response(
                {'error': f'Sayohatlar sonini oshirishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(PassengerDetailSerializer(passenger).data)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, telegram_id=None):
        """Faollik holatini o'zgartirish"""
        passenger = self.get_object()

        try:
            with transaction.atomic():
                passenger.is_active = not passenger.is_active
                passenger.save()
        except Exception as e:
            return Response(
                {'error': f'Status o\'zgartirishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        action = "faollashtirildi" if passenger.is_active else "faolsizlantirildi"
        return Response({
            'message': f'Yo\'lovchi {action}',
            'data': PassengerDetailSerializer(passenger).data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Umumiy statistika"""
        stats = Passenger.objects.aggregate(
            total_passengers=Count('id'),
            active_passengers=Count('id', filter=models.Q(is_active=True)),
            average_rating=Avg('rating'),
            total_trips=Sum('total_trips')
        )

        serializer = PassengerStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-telegram')
    def by_telegram(self, request):
        """Telegram ID bo'yicha qidirish (query param orqali)"""
        telegram_id = request.query_params.get('telegram_id')

        if not telegram_id:
            raise ValidationError({'error': 'telegram_id parametri talab qilinadi'})

        try:
            passenger = get_object_or_404(Passenger, telegram_id=telegram_id)
            serializer = PassengerDetailSerializer(passenger)
            return Response(serializer.data)
        except Passenger.DoesNotExist:
            raise NotFound({'error': 'Yo\'lovchi topilmadi'})

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Faol yo'lovchilar ro'yxati"""
        active_passengers = self.filter_queryset(
            self.get_queryset().filter(is_active=True)
        )

        page = self.paginate_queryset(active_passengers)
        if page is not None:
            serializer = PassengerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PassengerListSerializer(active_passengers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-update-status')
    def bulk_update_status(self, request):
        """Bir nechta yo'lovchi statusini yangilash"""
        telegram_ids = request.data.get('telegram_ids', [])
        is_active = request.data.get('is_active')

        if not telegram_ids:
            return Response(
                {'error': 'telegram_ids maydoni talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if is_active is None:
            return Response(
                {'error': 'is_active maydoni talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                updated_count = Passenger.objects.filter(
                    telegram_id__in=telegram_ids
                ).update(is_active=is_active)
        except Exception as e:
            return Response(
                {'error': f'Bulk update xatosi: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': f'{updated_count} ta yo\'lovchi yangilandi',
            'is_active': is_active
        })