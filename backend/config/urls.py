"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls), commenting out for now as we don't have admin setup
    #basic movie endpoints, no parameters necessary
    #j GET /api/movies/ - get all movies with details
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

#Help:
# Example Frontend Usage:
# fetch('/api/movies/')                    → get_all_movies()
# fetch('/api/movies/5/')                  → get_movie_details(request, movie_id=5)
# fetch('/api/movies/currently-running/')  → get_currently_running_movies()
# fetch('/api/movies/search/?q=spider')    → search_movies_by_name()
# fetch('/api/movies/genre/Action/')       → filter_movies_by_genre(request, genre_name='Action')
