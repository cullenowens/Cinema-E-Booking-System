#creates function for the route from urls.oy
#creates the logic responsible for processing a request, in this case,
#for admin tasks and responsibilities in the website
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.db.models import Count

from .models import Movie, Promotion, Profile, MovieShowtime
from .serializers import MovieSerializer, PromotionSerializer
from .events import event_bus, Event, EventTypes

import logging

logger = logging.getLogger(__name__)

#Managing Promotions
class AdminPromotionView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PromotionSerializer

    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        queryset = Promotion.objects.all()
#Managing Movies
class AdminMovieView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

# ADMIN AUTHENTICATION
class AdminLoginView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        remember_me = request.data.get('remember_me', False)

        # Authenticate user
        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is admin/staff
        if not user.is_staff:
            return Response(
                {"error": "Admin access required"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if user is active
        if not user.is_active:
            return Response(
                {"error": "Account is not active"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=7))

        # Publish admin login event
        event = Event(
            event_type=EventTypes.ADMIN_LOGIN,
            data={
                "username": user.username,
                "login_time": str(refresh.access_token.payload['iat'])
            },
            user=user.username
        )
        event_bus.publish(event)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff
            },
            "message": "Admin login successful"
        }, status=status.HTTP_200_OK)

# ADMIN HOME PAGE
class AdminHomeView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            # Get statistics
            total_movies = Movie.objects.count()
            currently_running = Movie.objects.filter(movie_status='Currently Running').count()
            coming_soon = Movie.objects.filter(movie_status='Coming Soon').count()
            active_promotions = Promotion.objects.filter(is_active=True).count()
            total_users = User.objects.count()
            active_users = Profile.objects.filter(status='Active').count()
            total_showtimes = MovieShowtime.objects.count()

            # Build menu structure
            menu_items = [
                {
                    "id": "manage_movies",
                    "label": "Manage Movies",
                    "description": "Add, edit, or remove movies from the system",
                    "icon": "film",
                    "endpoint": "/admin/movies/",
                    "count": total_movies
                },
                {
                    "id": "manage_promotions",
                    "label": "Manage Promotions",
                    "description": "Create and manage promotional offers",
                    "icon": "tag",
                    "endpoint": "/admin/promotions/",
                    "count": active_promotions
                },
                {
                    "id": "manage_users",
                    "label": "Manage Users",
                    "description": "View and manage user accounts",
                    "icon": "users",
                    "endpoint": "/admin/users/",
                    "count": total_users
                },
                {
                    "id": "manage_showtimes",
                    "label": "Manage Showtimes",
                    "description": "Schedule and manage movie showtimes",
                    "icon": "clock",
                    "endpoint": "/admin/showtimes/",
                    "count": total_showtimes
                }
            ]

            response_data = {
                "admin_info": {
                    "username": request.user.username,
                    "email": request.user.email
                },
                "menu_items": menu_items,
                "statistics": {
                    "total_movies": total_movies,
                    "currently_running": currently_running,
                    "coming_soon": coming_soon,
                    "active_promotions": active_promotions,
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_showtimes": total_showtimes
                }
            }

            # Log admin accessing home page
            event = Event(
                event_type=EventTypes.ADMIN_ACTION,
                data={"action": "viewed_admin_home"},
                user=request.user.username
            )
            event_bus.publish(event)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in AdminHomeView: {e}")
            return Response(
                {"error": "Failed to load admin home page"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
