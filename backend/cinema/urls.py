'''
The Purpose of this file is to define URL patterns for the Cinema E-Booking System backend.
The file maps URL patterns to view functions/classes.

URL Structure:
- /admin/*  -> Admin-specific endpoints for managing movies and promotions.
- /api/movies/*  -> Public API endpoints for retrieving movie information.
- /api/auth/*  -> Authentication and user profile management endpoints.
'''


# cinema/urls.py
#this defines the specific routes for the cinema app and actual endpoints to logic
#will only handle urls that config/urls.py sends to it
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views, views_admin, views_auth

urlpatterns = [
    # ADMIN ENDPOINTS
    #Admin Movies
    path('admin/movies/', views_admin.AdminMovieView.as_view(), name='admin-add-movie'),        # POST to add
    path('admin/movies/<int:pk>/', views_admin.AdminMovieView.as_view(), name='admin-remove-movie'),  # DELETE to remove
    #Admin Promotions
    path('admin/promotions/', views_admin.AdminPromotionView.as_view(), name='admin-add-promotion'),       # POST to add
    path('admin/promotions/<int:pk>/', views_admin.AdminPromotionView.as_view(), name='admin-remove-promotion'),  # DELETE to remove

    # Admin Authentication
    path('api/admin/login/', csrf_exempt(views_admin.AdminLoginView.as_view()), name='admin-login'),
    # Admin Home Page
    path('api/admin/home/', views_admin.AdminHomeView.as_view(), name='admin-home'),
    # Admin Movie Management
    path('api/admin/movies/', views_admin.AdminMovieListView.as_view(), name='admin-list-movies'),           # GET all movies
    path('api/admin/movies/create/', views_admin.AdminMovieCreateView.as_view(), name='admin-create-movie'),  # POST to create
    path('api/admin/movies/<int:pk>/', views_admin.AdminMovieDetailView.as_view(), name='admin-movie-detail'),  # GET/PUT/DELETE specific movie
    
    # Admin Genre List (for dropdown in add movie form)
    path('api/admin/genres/', views_admin.AdminGenreListView.as_view(), name='admin-genres'),
    
    # Admin Promotion Management
    path('api/admin/promotions/', views_admin.AdminPromotionListView.as_view(), name='admin-promotions-list'),
    path('api/admin/promotions/create/', views_admin.AdminPromotionCreateView.as_view(), name='admin-promotions-create'),
    path('api/admin/promotions/<int:pk>/', views_admin.AdminPromotionDetailView.as_view(), name='admin-promotions-detail'),
    path('api/admin/promotions/<int:pk>/send-email/', views_admin.AdminPromotionEmailView.as_view(), name='admin-promotions-email'),

    # Admin Showroom Management
    path('api/admin/showrooms/', views_admin.AdminShowroomListView.as_view(), name='admin-showrooms'),
    
    # Admin Showing Management (Schedule Movies)
    path('api/admin/showings/', views_admin.AdminShowingListView.as_view(), name='admin-showings-list'),
    path('api/admin/showings/create/', views_admin.AdminShowingCreateView.as_view(), name='admin-showings-create'),
    path('api/admin/showings/availability/', views_admin.AdminShowingAvailabilityView.as_view(), name='admin-showings-availability'),
    path('api/admin/showings/<int:pk>/', views_admin.AdminShowingDetailView.as_view(), name='admin-showings-detail'),

    # PUBLIC MOVIE ENDPOINTS
    #basic movie endpoints, no parameters necessary
    #GET /api/movies/ - get all movies with details
    path('api/movies/', views.get_all_movies, name='get_all_movies'),
    #GET /api/movies/currently_running - get currently running movies
    path('api/movies/currently_running/', views.get_currently_running_movies, name='currently_running'),
    #GET /api/movies/coming-soon/ - get coming soon movies
    path('api/movies/coming-soon/', views.get_coming_soon_movies, name='coming_soon'),
    #GET /api/movies/search/ - search movies by title
    path('api/movies/search/', views.search_movies_by_name, name='search_movies'),
    # Dynamic URL with parameter - captures movie ID from URL
    # ex. GET /api/movies/5/ - Returns details for movie with ID 5
    path('api/movies/<int:movie_id>/', views.get_movie_details, name='movie_details'),
    # Dynamic URL with string parameter for genre filtering
    # ex. GET /api/movies/genre/Action/ - Returns all Action movies
    path('api/movies/genre/<str:genre_name>/', views.filter_movies_by_genre, name='filter_by_genre'),
]

# AUTHENTICATION & PROFILE ENDPOINTS
from .views_auth import RegisterView, LoginView, LogoutView, ProfileView, verify_email, ForgotPasswordView, ResetPasswordView, UserDetailSerializer

urlpatterns += [
    #POST path to register + first name, last name, password, subscribed
    # User Registration - POST /api/auth/register/
    # Creates new user account and sends verification email
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    #POST + username, password, *remember me*?

    # User Login - POST /api/auth/login/
    # Authenticates user and returns JWT tokens
    path("api/auth/login/", LoginView.as_view(), name="login"),
    #POST path

    # User Logout - POST /api/auth/logout/
    # Blacklists refresh token to invalidate session
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    #GET + auth token path to get user profile info

     # User Profile - GET/PUT /api/auth/profile/
    # GET: Retrieve user profile info | PUT: Update profile info
    path("api/auth/profile/", ProfileView.as_view(), name="profile"),
    #We need an update profile path too
    #PUT + auth token path to update user profile info
    #GET then check token "?token=..."

    # Email Verification - POST /api/auth/verify/
    # Verifies user email with 6-digit code (expires in 5 minutes)
    path('api/auth/verify/', verify_email, name='verify_email'),
    #POST then use the email the user inputs

    # Forgot Password - POST /api/auth/forgot-password/
    # Sends password reset code to user's email
    path('api/auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    #POST then use the token and new password the user inputs

    # Reset Password - POST /api/auth/reset-password/
    # Resets password
    path('api/auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    #change password - POST /api/auth/change-password/
    #changes password for users when they're logged in
    path('api/auth/change-password/', views_auth.ChangePasswordView.as_view(), name='change_password'),

     # User Address - GET/POST/PUT /api/auth/address/
    # Manage user's billing address (one per user)
    path('api/auth/address/', views_auth.AddressView.as_view(), name='address'),
    
    # Payment Cards - GET/POST /api/auth/payment-cards/
    # List all cards or add new payment card (max 4 per user, encrypted storage)
    path('api/auth/payment-cards/', views_auth.PaymentCardView.as_view(), name='payment_cards'),

    # Payment Card Detail - GET/PUT/DELETE /api/auth/payment-cards/<id>/
    # Retrieve, update, or delete specific payment card
    path('api/auth/payment-cards/<int:pk>/', views_auth.PaymentCardDetailView.as_view(), name='payment_card_detail'),

    # User Details - GET /api/auth/user-details/
    # Retrieve basic user details
    #path('api/auth/user-details/', views_auth.UserDetailView.as_view(), name='user_details'),
]

# USER PORTAL ENDPOINTS SUMMARY
from .views_user import (
    ShowingListView,
    ShowingDetailView,
    SeatMapView,
    SeatAvailabilityView,
    BookingCreateView,
    BookingListView,
    BookingDetailView,
    MovieShowingsView,
)

urlpatterns += [
    # Browse Showings - Public access
    path('api/user/showings/', ShowingListView.as_view(), name='user-showing-list'),
    path('api/user/showings/<int:pk>/', ShowingDetailView.as_view(), name='user-showing-detail'),

    # Seat Selection - Public access (can view before login)
    path('api/user/showings/<int:pk>/seats/', SeatMapView.as_view(), name='seat-map'),
    path('api/user/showings/<int:pk>/check-seats/', SeatAvailabilityView.as_view(), name='check-seats'),

    # Bookings - Requires authentication
    path('api/user/bookings/', BookingListView.as_view(), name='user-booking-list'),
    path('api/user/bookings/create/', BookingCreateView.as_view(), name='booking-create'),
    path('api/user/bookings/<int:pk>/', BookingDetailView.as_view(), name='user-booking-detail'),

    # Browse by Movie - Public access
    path('api/user/movies/<int:movie_id>/showings/', MovieShowingsView.as_view(), name='movie-showings'),
]

#Help:
# Example Frontend Usage:
# fetch('/api/movies/')                    → get_all_movies()
# fetch('/api/movies/5/')                  → get_movie_details(request, movie_id=5)
# fetch('/api/movies/currently-running/')  → get_currently_running_movies()
# fetch('/api/movies/search/?q=spider')    → search_movies_by_name()
# fetch('/api/movies/genre/Action/')       → filter_movies_by_genre(request, genre_name='Action')



# ADMIN ENDPOINTS SUMMARY
# 
# Authentication:
# POST   /api/admin/login/                     → Admin login
# 
# Dashboard:
# GET    /api/admin/home/                      → Admin home with menu & stats
# 
# Movies:
# GET    /api/admin/movies/                    → List all movies
# POST   /api/admin/movies/create/             → Create movie
# GET    /api/admin/movies/<id>/               → Get movie details
# PUT    /api/admin/movies/<id>/               → Update movie
# DELETE /api/admin/movies/<id>/               → Delete movie
# GET    /api/admin/genres/                    → List genres
# 
# Showrooms:
# GET    /api/admin/showrooms/                 → List showrooms
# 
# Showings (Schedule):
# GET    /api/admin/showings/                  → List showings (filters: movie_id, showroom_id, date)
# POST   /api/admin/showings/create/           → Schedule movie
# GET    /api/admin/showings/<id>/             → Get showing details
# PUT    /api/admin/showings/<id>/             → Update showing
# DELETE /api/admin/showings/<id>/             → Delete showing
# GET    /api/admin/showings/availability/     → Check availability
# 
# Promotions:
# GET    /api/admin/promotions/                → List all promotions
# POST   /api/admin/promotions/                → Add new promotion
# DELETE /api/admin/promotions/1/              → Delete promotion with ID 1