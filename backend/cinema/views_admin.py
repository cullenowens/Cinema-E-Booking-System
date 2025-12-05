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
from django.db.models import Q
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
import os

from .models import Movie, Promotion, Profile, MovieShowtime, Genre, MovieGenre, Showroom, Showing
from .serializers import MovieSerializer, PromotionSerializer, ShowingSerializer, ShowroomSerializer

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
class AdminPromotionListView(APIView):
    """
    List all promotions
    
    GET /api/admin/promotions/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get all promotions ordered by creation date"""
        try:
            promotions = Promotion.objects.all().order_by('-created_at')
            serializer = PromotionSerializer(promotions, many=True)
            
            return Response({
                'count': len(serializer.data),
                'promotions': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving promotions: {e}")
            return Response(
                {"error": "Failed to retrieve promotions"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class AdminPromotionCreateView(APIView):
    '''
    creates a new promotion and optionally emails it to subscribed users
    
    purpose is admin create promotional discount codes for users to apply at checkout
    
    POST /api/admin/promotions/create/
    
    Request body:
    {
        "promo_code": "SUMMER2026",
        "discount_type": "percentage",  # "percentage" or "fixed"
        "discount_value": 20.00,  # 20.00 for 20% OR $20 depending on discount_type
        "start_date": "2026-06-01",
        "end_date": "2026-08-31",
        "send_email": true  # optional, defaults to false
    }
    
    Response:
    {
        "message": "Promotion created successfully",
        "promotion": {
            "promo_id": 3,
            "promo_code": "SUMMER2026",
            "discount_type": "percentage",
            "discount_value": 20.00,
            "start_date": "2026-06-01",
            "end_date": "2026-08-31"
        },
        "emails_sent": 45,
        "email_message": "Promotion email sent to 45 subscribed users"
    }
    '''
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Create a new promotion with validation"""
        try:
            # Extract send_email flag (not part of model)
            send_email_flag = request.data.pop('send_email', False)
            
            serializer = PromotionSerializer(data=request.data)
            
            if serializer.is_valid():
                promotion = serializer.save()
                
                logger.info(
                    f"Promotion created: {promotion.promo_code} "
                    f"({promotion.discount_type}: {promotion.discount_value}) "
                    f"by admin {request.user.username}"
                )
                
                # Send emails to subscribed users if requested
                emails_sent = 0
                if send_email_flag:
                    emails_sent = self.send_promotion_emails(promotion)
                
                response_data = {
                    'message': 'Promotion created successfully',
                    'promotion': PromotionSerializer(promotion).data
                }
                
                if send_email_flag:
                    response_data['emails_sent'] = emails_sent
                    response_data['email_message'] = f'Promotion email sent to {emails_sent} subscribed users'
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            # Return validation errors
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating promotion: {e}")
            return Response(
                {"error": f"Failed to create promotion: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def send_promotion_emails(self, promotion):
        """send promotion email to all subscribed users"""
        # get all users who are subscribed to promotions
        subscribed_users = User.objects.filter(
            profile__subscribed=True,
            is_active=True
        ).exclude(email='')
        
        emails_sent = 0
        
        # build email based on discount type
        if promotion.discount_type == 'percentage':
            subject = f"🎉 special offer: {promotion.discount_value:.0f}% off!"
            discount_text = f"{promotion.discount_value:.0f}% OFF"
        else:
            subject = f"🎉 special offer: ${promotion.discount_value:.2f} off!"
            discount_text = f"${promotion.discount_value:.2f} OFF"
        
        message = f"""
hello!

we have an exciting promotion for you!

promo code: {promotion.promo_code}
discount: {discount_text}
valid from: {promotion.start_date.strftime('%B %d, %Y')}
valid until: {promotion.end_date.strftime('%B %d, %Y')}

use code \"{promotion.promo_code}\" at checkout to save on your ticket purchase!

don't miss out on this limited-time offer!

best regards,
cinema e-booking team

---
you're receiving this email because you subscribed to promotional offers
to unsubscribe, please update your profile settings
        """
        
        for user in subscribed_users:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    #from_email=settings.DEFAULT_FROM_EMAIL,
                    from_email=os.getenv("GMAIL_EMAIL"),
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                emails_sent += 1
                logger.info(f"Promotion email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {e}")
                continue
        
        logger.info(f"Promotion emails sent: {emails_sent} out of {subscribed_users.count()} subscribed users")
        
        return emails_sent
    
class AdminPromotionDetailView(APIView):
    '''
    get, update, or delete a specific promotion
    
    purpose is admin manage existing promotional codes
    
    GET /api/admin/promotions/<id>/
    
    PUT /api/admin/promotions/<id>/
    Request body (all fields optional for partial update):
    {
        "promo_code": "UPDATED2026",
        "discount_type": "fixed",
        "discount_value": 15.00,
        "start_date": "2026-06-01",
        "end_date": "2026-09-30"
    }
    
    DELETE /api/admin/promotions/<id>/
    '''
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, pk):
        """Get promotion details"""
        try:
            promotion = Promotion.objects.get(pk=pk)
            serializer = PromotionSerializer(promotion)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Promotion.DoesNotExist:
            return Response(
                {"error": "Promotion not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving promotion: {e}")
            return Response(
                {"error": "Failed to retrieve promotion"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, pk):
        """Update promotion"""
        try:
            promotion = Promotion.objects.get(pk=pk)
            
            # Remove send_email flag if present (not for updates)
            request.data.pop('send_email', None)
            
            serializer = PromotionSerializer(promotion, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_promotion = serializer.save()
                
                logger.info(
                    f"Promotion updated: {updated_promotion.promo_code} "
                    f"({updated_promotion.discount_type}: {updated_promotion.discount_value}) "
                    f"by admin {request.user.username}"
                )
                
                return Response({
                    'message': 'Promotion updated successfully',
                    'promotion': PromotionSerializer(updated_promotion).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Promotion.DoesNotExist:
            return Response(
                {"error": "Promotion not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating promotion: {e}")
            return Response(
                {"error": f"Failed to update promotion: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """Delete promotion"""
        try:
            promotion = Promotion.objects.get(pk=pk)
            promo_code = promotion.promo_code
            
            promotion.delete()
            
            logger.info(f"Promotion deleted: {promo_code} by admin {request.user.username}")
            
            return Response({
                'message': f'Promotion "{promo_code}" deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Promotion.DoesNotExist:
            return Response(
                {"error": "Promotion not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting promotion: {e}")
            return Response(
                {"error": "Failed to delete promotion"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminPromotionEmailView(APIView):
    '''
    sends existing promotion email to all subscribed users
    
    purpose is admin manually trigger promotion email for existing promo code
    
    POST /api/admin/promotions/<id>/send-email/
    
    Response:
    {
        "message": "Promotion email sent to 45 subscribed users",
        "emails_sent": 45,
        "total_subscribed": 50
    }
    '''
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, pk):
        """send promotion email to subscribed users"""
        try:
            promotion = Promotion.objects.get(pk=pk)
            
            # get subscribed users
            subscribed_users = User.objects.filter(
                profile__subscribed=True,
                is_active=True
            ).exclude(email='')
            
            if subscribed_users.count() == 0:
                return Response({
                    'message': 'no subscribed users to send email to',
                    'emails_sent': 0
                }, status=status.HTTP_200_OK)
            
            # send emails
            emails_sent = 0
            
            # build email based on discount type
            if promotion.discount_type == 'percentage':
                subject = f"🎉 special offer: {promotion.discount_value:.0f}% off!"
                discount_text = f"{promotion.discount_value:.0f}% OFF"
            else:
                subject = f"🎉 special offer: ${promotion.discount_value:.2f} off!"
                discount_text = f"${promotion.discount_value:.2f} OFF"
            
            message = f"""
hello!

we have an exciting promotion for you!

promo code: {promotion.promo_code}
discount: {discount_text}
valid from: {promotion.start_date.strftime('%B %d, %Y')}
valid until: {promotion.end_date.strftime('%B %d, %Y')}

use code \"{promotion.promo_code}\" at checkout to save on your ticket purchase!

don't miss out on this limited-time offer!

best regards,
cinema e-booking team

---
you're receiving this email because you subscribed to promotional offers
to unsubscribe, please update your profile settings
            """
            
            for user in subscribed_users:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    emails_sent += 1
                except Exception as e:
                    logger.error(f"Failed to send email to {user.email}: {e}")
                    continue
            
            logger.info(
                f"Promotion {promotion.promo_code} emailed to {emails_sent} users "
                f"by admin {request.user.username}"
            )
            
            return Response({
                'message': f'Promotion email sent to {emails_sent} subscribed users',
                'emails_sent': emails_sent,
                'total_subscribed': subscribed_users.count()
            }, status=status.HTTP_200_OK)
            
        except Promotion.DoesNotExist:
            return Response(
                {"error": "Promotion not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error sending promotion emails: {e}")
            return Response(
                {"error": f"Failed to send emails: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ADD SHOWROOM MANAGEMENT  
class AdminShowroomListView(APIView):
    """
    Get all showrooms
    
    GET /api/admin/showrooms/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get all showrooms for dropdown selection"""
        try:
            showrooms = Showroom.objects.all().order_by('showroom_name')
            serializer = ShowroomSerializer(showrooms, many=True)
            
            return Response({
                'count': len(serializer.data),
                'showrooms': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving showrooms: {e}")
            return Response(
                {"error": "Failed to retrieve showrooms"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminShowingListView(APIView):
    """
    List all showings with optional filters
    
    GET /api/admin/showings/
    Query params:
    - movie_id: Filter by movie
    - showroom_id: Filter by showroom
    - date: Filter by date (YYYY-MM-DD)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get all showings with optional filtering"""
        try:
            showings = Showing.objects.all().select_related('movie', 'showroom')
            
            # Apply filters
            movie_id = request.query_params.get('movie_id')
            if movie_id:
                showings = showings.filter(movie_id=movie_id)
            
            showroom_id = request.query_params.get('showroom_id')
            if showroom_id:
                showings = showings.filter(showroom_id=showroom_id)
            
            date_str = request.query_params.get('date')
            if date_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    showings = showings.filter(start_time__date=date)
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Order by start time
            showings = showings.order_by('start_time')
            
            # Serialize
            serializer = ShowingSerializer(showings, many=True)
            
            return Response({
                'count': len(serializer.data),
                'showings': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving showings: {e}")
            return Response(
                {"error": "Failed to retrieve showings"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminShowingCreateView(APIView):
    """
    Create a new showing (schedule a movie)
    
    POST /api/admin/showings/create/
    
    Request body:
    {
        "movie_id": 1,
        "showroom_id": 1,
        "start_time": "2025-12-25T19:00:00",
        "end_time": "2025-12-25T21:30:00"  // optional
    }
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Create a new showing with conflict detection"""
        try:
            serializer = ShowingSerializer(data=request.data)
            
            if serializer.is_valid():
                showing = serializer.save()
                
                logger.info(
                    f"Showing created: {showing.movie.movie_title} in "
                    f"{showing.showroom.showroom_name} at {showing.start_time} "
                    f"by admin {request.user.username}"
                )
                
                return Response({
                    'message': 'Showing scheduled successfully',
                    'showing': ShowingSerializer(showing).data
                }, status=status.HTTP_201_CREATED)
            
            # Return validation errors (including conflict errors)
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating showing: {e}")
            return Response(
                {"error": f"Failed to create showing: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminShowingDetailView(APIView):
    """
    Get, update, or delete a specific showing
    
    GET /api/admin/showings/<id>/
    PUT /api/admin/showings/<id>/
    DELETE /api/admin/showings/<id>/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, pk):
        """Get showing details"""
        try:
            showing = Showing.objects.select_related('movie', 'showroom').get(pk=pk)
            serializer = ShowingSerializer(showing)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Showing.DoesNotExist:
            return Response(
                {"error": "Showing not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving showing: {e}")
            return Response(
                {"error": "Failed to retrieve showing"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, pk):
        """Update showing"""
        try:
            showing = Showing.objects.get(pk=pk)
            serializer = ShowingSerializer(showing, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_showing = serializer.save()
                
                logger.info(
                    f"Showing updated: {updated_showing.movie.movie_title} "
                    f"by admin {request.user.username}"
                )
                
                return Response({
                    'message': 'Showing updated successfully',
                    'showing': ShowingSerializer(updated_showing).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Showing.DoesNotExist:
            return Response(
                {"error": "Showing not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating showing: {e}")
            return Response(
                {"error": f"Failed to update showing: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """Delete showing"""
        try:
            showing = Showing.objects.select_related('movie', 'showroom').get(pk=pk)
            showing_info = f"{showing.movie.movie_title} in {showing.showroom.showroom_name} at {showing.start_time}"
            
            showing.delete()
            
            logger.info(f"Showing deleted: {showing_info} by admin {request.user.username}")
            
            return Response({
                'message': f'Showing deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Showing.DoesNotExist:
            return Response(
                {"error": "Showing not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting showing: {e}")
            return Response(
                {"error": "Failed to delete showing"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminShowingAvailabilityView(APIView):
    """
    Check showroom availability for a given date/time
    
    GET /api/admin/showings/availability/
    Query params:
    - showroom_id: Required
    - start_time: Required (ISO format: 2025-12-25T19:00:00)
    - end_time: Optional (defaults to start_time + 2.5 hours)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Check if a showroom is available at given time"""
        try:
            showroom_id = request.query_params.get('showroom_id')
            start_time_str = request.query_params.get('start_time')
            end_time_str = request.query_params.get('end_time')
            
            if not showroom_id or not start_time_str:
                return Response({
                    "error": "showroom_id and start_time are required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse times
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                if end_time_str:
                    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                else:
                    end_time = start_time + timedelta(hours=2, minutes=30)
            except ValueError:
                return Response({
                    "error": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for conflicts
            conflicts = Showing.objects.filter(
                showroom_id=showroom_id
            ).filter(
                Q(start_time__lt=end_time, end_time__gt=start_time) |
                Q(start_time__gte=start_time, start_time__lt=end_time)
            ).select_related('movie')
            
            if conflicts.exists():
                conflict_list = [{
                    'movie_title': c.movie.movie_title,
                    'start_time': c.start_time.isoformat(),
                    'end_time': c.end_time.isoformat()
                } for c in conflicts]
                
                return Response({
                    'available': False,
                    'conflicts': conflict_list
                }, status=status.HTTP_200_OK)
            
            return Response({
                'available': True,
                'message': 'Showroom is available for the requested time'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return Response(
                {"error": "Failed to check availability"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )