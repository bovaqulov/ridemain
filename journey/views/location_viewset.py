# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from ..models.location import Location, UserLocation
from ..serializers.location_serializer import (
    UserLocationCreateSerializer,
    UserLocationSerializer
)


class LocationViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='create-user-location')
    def create_user_location(self, request):
        """
        Foydalanuvchi uchun yangi lokatsiya yaratish
        POST /api/locations/create-user-location/
        {
            "telegram_id": 123456789,
            "coordinate": {"lat": 41.311081, "lng": 69.240562},
            "accuracy": 10.5,
            "live_period": 60,
            "heading": 90
        }
        """
        serializer = UserLocationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        telegram_id = serializer.validated_data['telegram_id']
        name = serializer.validated_data.get("name")
        coordinate = serializer.validated_data['coordinate']
        accuracy = serializer.validated_data.get('accuracy')
        live_period = serializer.validated_data.get('live_period')
        heading = serializer.validated_data.get('heading')

        lat = coordinate['lat']
        lng = coordinate['lng']

        try:
            with transaction.atomic():
                # 1. Locationni topish yoki yaratish
                location, created = Location.objects.get_or_create(
                    lat=lat,
                    lng=lng,
                    defaults={
                        'name': name
                    }
                )

                # 2. UserLocation yaratish
                user_location = UserLocation.objects.create(
                    user=telegram_id,
                    location=location,
                    accuracy=accuracy,
                    live_period=live_period,
                    heading=heading
                )

                response_data = {
                    'success': True,
                    'message': 'User location created successfully',
                    'user_location': UserLocationSerializer(user_location).data,
                    'location_created': created
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='user-locations/(?P<telegram_id>[^/.]+)')
    def user_locations(self, request, telegram_id=None):
        """
        Foydalanuvchining barcha joylashuvlarini olish
        GET /api/locations/user-locations/123456789/
        """
        try:
            telegram_id = int(telegram_id)
            user_locations = UserLocation.objects.filter(
                user=telegram_id
            ).select_related('location').order_by('-created_at')

            serializer = UserLocationSerializer(user_locations, many=True)

            return Response({
                'success': True,
                'telegram_id': telegram_id,
                'locations': serializer.data,
                'total_count': user_locations.count()
            })

        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid telegram_id format'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='user-latest/(?P<telegram_id>[^/.]+)')
    def user_latest_location(self, request, telegram_id=None):
        """
        Foydalanuvchining oxirgi joylashuvini olish
        GET /api/locations/user-latest/123456789/
        """
        try:
            telegram_id = int(telegram_id)
            latest_location = UserLocation.objects.filter(
                user=telegram_id
            ).select_related('location').order_by('-created_at').first()

            if not latest_location:
                return Response({
                    'success': True,
                    'message': 'No locations found for user',
                    'location': None
                })

            serializer = UserLocationSerializer(latest_location)

            return Response({
                'success': True,
                'telegram_id': telegram_id,
                'location': serializer.data
            })

        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid telegram_id format'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['delete'], url_path='delete-user-locations/(?P<telegram_id>[^/.]+)')
    def delete_user_locations(self, request, telegram_id=None):
        """
        Foydalanuvchining barcha joylashuvlarini o'chirish
        DELETE /api/locations/delete-user-locations/123456789/
        """
        try:
            telegram_id = int(telegram_id)
            deleted_count, _ = UserLocation.objects.filter(user=telegram_id).delete()

            return Response({
                'success': True,
                'message': f'Deleted {deleted_count} user locations',
                'deleted_count': deleted_count
            })

        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid telegram_id format'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)