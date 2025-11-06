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
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    #POST + username, password, *remember me*?
    path("api/auth/login/", LoginView.as_view(), name="login"),
    #POST path
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    #GET + auth token path to get user profile info
    path("api/auth/profile/", ProfileView.as_view(), name="profile"),
    #We need an update profile path too
    #PUT + auth token path to update user profile info
    #GET then check token "?token=..."
    path('api/auth/verify/', verify_email, name='verify_email'),
    #POST then use the email the user inputs
    path('api/auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    #POST then use the token and new password the user inputs
    path('api/auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    #multiple potential endpoints for user address management
    #GET (get current address), POST(create new), PUT(update), DELETE for user address
    path('api/auth/address/', views_auth.AddressView.as_view(), name='address'),
    
    #GET or POST + brand, expiration, card no.
    path('api/auth/payment-cards/', views_auth.PaymentCardView.as_view(), name='payment_cards'),
    path('api/auth/payment-cards/<int:pk>/', views_auth.PaymentCardDetailView.as_view(), name='payment_card_detail'),
]

#Help:
# Example Frontend Usage:
# fetch('/api/movies/')                    → get_all_movies()
# fetch('/api/movies/5/')                  → get_movie_details(request, movie_id=5)
# fetch('/api/movies/currently-running/')  → get_currently_running_movies()
# fetch('/api/movies/search/?q=spider')    → search_movies_by_name()
# fetch('/api/movies/genre/Action/')       → filter_movies_by_genre(request, genre_name='Action')