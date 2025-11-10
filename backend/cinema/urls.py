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
from . import views, views_admin, views_auth

urlpatterns = [
    #Admin Movies
    path('admin/movies/', views_admin.AdminMovieView.as_view(), name='admin-add-movie'),        # POST to add
    path('admin/movies/<int:pk>/', views_admin.AdminMovieView.as_view(), name='admin-remove-movie'),  # DELETE to remove
    #Admin Promotions
    path('admin/promotions/', views_admin.AdminPromotionView.as_view(), name='admin-add-promotion'),       # POST to add
    path('admin/promotions/<int:pk>/', views_admin.AdminPromotionView.as_view(), name='admin-remove-promotion'),  # DELETE to remove
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
from .views_auth import RegisterView, LoginView, LogoutView, ProfileView, verify_email, ForgotPasswordView, ResetPasswordView

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
]

#Help:
# Example Frontend Usage:
# fetch('/api/movies/')                    → get_all_movies()
# fetch('/api/movies/5/')                  → get_movie_details(request, movie_id=5)
# fetch('/api/movies/currently-running/')  → get_currently_running_movies()
# fetch('/api/movies/search/?q=spider')    → search_movies_by_name()
# fetch('/api/movies/genre/Action/')       → filter_movies_by_genre(request, genre_name='Action')