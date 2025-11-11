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

from .models import Movie, Promotion, Profile, MovieShowtime, Genre, MovieGenre
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
        # NOT USING EVENTS ANYMORE
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
            active_promotions = Promotion.objects.count()
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

            logger.info(f"Admin home page accessed by: {request.user.username}")

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in AdminHomeView: {e}")
            return Response(
                {"error": "Failed to load admin home page"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# MOVIE MANAGEMENT
class AdminMovieListView(APIView):
    """
    List all movies for admin
    
    GET /api/admin/movies/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get all movies with their genres"""
        try:
            movies = Movie.objects.all().order_by('-movie_id')
            movies_data = []
            
            for movie in movies:
                # Get genres for this movie
                genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
                
                movies_data.append({
                    'movie_id': movie.movie_id,
                    'movie_title': movie.movie_title,
                    'movie_description': movie.movie_description,
                    'age_rating': movie.age_rating,
                    'poster_url': movie.poster_url,
                    'trailer_url': movie.trailer_url,
                    'movie_status': movie.movie_status,
                    'genres': list(genres)
                })
            
            return Response({
                'count': len(movies_data),
                'movies': movies_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in AdminMovieListView: {e}")
            return Response(
                {"error": "Failed to retrieve movies"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminMovieCreateView(APIView):
    """
    Create a new movie
    
    POST /api/admin/movies/create/
    
    Request body:
    {
        "movie_title": "Spider-Man: No Way Home",
        "movie_description": "Peter Parker's secret identity is revealed...",
        "age_rating": "PG-13",
        "poster_url": "https://example.com/poster.jpg",
        "trailer_url": "https://youtube.com/watch?v=...",
        "movie_status": "Currently Running",
        "genres": ["Action", "Adventure", "Sci-Fi"]
    }
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Create a new movie with validation"""
        try:
            serializer = MovieSerializer(data=request.data)
            
            if serializer.is_valid():
                movie = serializer.save()
                
                # Get the created movie with genres
                genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
                
                logger.info(f"Movie created: {movie.movie_title} by admin {request.user.username}")
                
                return Response({
                    'message': 'Movie created successfully',
                    'movie': {
                        'movie_id': movie.movie_id,
                        'movie_title': movie.movie_title,
                        'movie_description': movie.movie_description,
                        'age_rating': movie.age_rating,
                        'poster_url': movie.poster_url,
                        'trailer_url': movie.trailer_url,
                        'movie_status': movie.movie_status,
                        'genres': list(genres)
                    }
                }, status=status.HTTP_201_CREATED)
            
            # Return validation errors
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating movie: {e}")
            return Response(
                {"error": f"Failed to create movie: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminMovieDetailView(APIView):
    """
    Get, update, or delete a specific movie
    
    GET /api/admin/movies/<id>/
    PUT /api/admin/movies/<id>/
    DELETE /api/admin/movies/<id>/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, pk):
        """Get movie details"""
        try:
            movie = Movie.objects.get(pk=pk)
            genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
            
            return Response({
                'movie_id': movie.movie_id,
                'movie_title': movie.movie_title,
                'movie_description': movie.movie_description,
                'age_rating': movie.age_rating,
                'poster_url': movie.poster_url,
                'trailer_url': movie.trailer_url,
                'movie_status': movie.movie_status,
                'genres': list(genres)
            }, status=status.HTTP_200_OK)
            
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving movie: {e}")
            return Response(
                {"error": "Failed to retrieve movie"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, pk):
        """Update movie"""
        try:
            movie = Movie.objects.get(pk=pk)
            serializer = MovieSerializer(movie, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_movie = serializer.save()
                genres = Genre.objects.filter(moviegenre__movie=updated_movie).values_list('genre_name', flat=True)
                
                logger.info(f"Movie updated: {updated_movie.movie_title} by admin {request.user.username}")
                
                return Response({
                    'message': 'Movie updated successfully',
                    'movie': {
                        'movie_id': updated_movie.movie_id,
                        'movie_title': updated_movie.movie_title,
                        'movie_description': updated_movie.movie_description,
                        'age_rating': updated_movie.age_rating,
                        'poster_url': updated_movie.poster_url,
                        'trailer_url': updated_movie.trailer_url,
                        'movie_status': updated_movie.movie_status,
                        'genres': list(genres)
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating movie: {e}")
            return Response(
                {"error": f"Failed to update movie: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """Delete movie"""
        try:
            movie = Movie.objects.get(pk=pk)
            movie_title = movie.movie_title
            
            # Delete associated genres first (CASCADE should handle this, but being explicit)
            MovieGenre.objects.filter(movie=movie).delete()
            
            # Delete the movie
            movie.delete()
            
            logger.info(f"Movie deleted: {movie_title} by admin {request.user.username}")
            
            return Response({
                'message': f'Movie "{movie_title}" deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting movie: {e}")
            return Response(
                {"error": "Failed to delete movie"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminGenreListView(APIView):
    """
    Get all available genres
    
    GET /api/admin/genres/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get all genres"""
        try:
            genres = Genre.objects.all().order_by('genre_name')
            genre_list = [{'genre_id': g.genre_id, 'genre_name': g.genre_name} for g in genres]
            
            return Response({
                'count': len(genre_list),
                'genres': genre_list
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving genres: {e}")
            return Response(
                {"error": "Failed to retrieve genres"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# PROMOTION MANAGEMENT
class AdminPromotionView(generics.CreateAPIView, generics.DestroyAPIView):
    """
    Admin promotion management
    
    POST /api/admin/promotions/ - Create new promotion
    DELETE /api/admin/promotions/<id>/ - Delete promotion
    """
    permission_classes = [IsAdminUser]
    serializer_class = PromotionSerializer
    queryset = Promotion.objects.all()

# ============================================================================
# PLACEHOLDER VIEWS FOR USER AND SHOWTIME MANAGEMENT
# These will be implemented in future updates
# ============================================================================

class AdminUserManagementView(APIView):
    """
    Placeholder for user management functionality
    Will be implemented in future update
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({
            "message": "User management coming soon",
            "available_actions": ["view_users", "change_user_status", "delete_users"]
        })


class AdminShowtimeManagementView(APIView):
    """
    Placeholder for showtime management functionality
    Will be implemented in future update
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({
            "message": "Showtime management coming soon",
            "available_actions": ["create_showtime", "update_showtime", "delete_showtime"]
        })