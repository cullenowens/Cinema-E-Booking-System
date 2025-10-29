# cinema/urls.py
from django.urls import path
from . import views, admin_views

urlpatterns = [
    #Admin Movies
    path('admin/movies/', admin_views.AdminMovieView.as_view(), name='admin-add-movie'),        # POST to add
    path('admin/movies/<int:pk>/', admin_views.AdminMovieView.as_view(), name='admin-remove-movie'),  # DELETE to remove
    #Admin Promotions
    path('admin/promotions/', admin_views.AdminPromotionView.as_view(), name='admin-add-promotion'),       # POST to add
    path('admin/promotions/<int:pk>/', admin_views.AdminPromotionView.as_view(), name='admin-remove-promotion'),  # DELETE to remove
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
from .views_auth import RegisterView, LoginView, LogoutView, ProfileView, verify_email

urlpatterns += [
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/profile/", ProfileView.as_view(), name="profile"),
    path('api/auth/verify/', verify_email, name='verify_email'),
]

#Help:
# Example Frontend Usage:
# fetch('/api/movies/')                    → get_all_movies()
# fetch('/api/movies/5/')                  → get_movie_details(request, movie_id=5)
# fetch('/api/movies/currently-running/')  → get_currently_running_movies()
# fetch('/api/movies/search/?q=spider')    → search_movies_by_name()
# fetch('/api/movies/genre/Action/')       → filter_movies_by_genre(request, genre_name='Action')