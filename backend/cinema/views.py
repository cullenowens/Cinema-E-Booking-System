#creates function for the route
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Movie, Genre, MovieGenre, MovieShowtime

@require_http_methods(["GET"])
def get_all_movies(request):
    """Get all movies w details"""
    movies = Movie.objects.all()
    data = []

    for movie in movies:
        #for each movie, get its genre and showtime(s)
        genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
        showtimes = MovieShowtime.objects.filter(movie=movie).values_list('showtime_value', flat=True)
        #build a dict
        data.append({
            'movie_id': movie.movie_id,
            'movie_title': movie.movie_title,
            'movie_description': movie.movie_description,
            'age_rating': movie.age_rating,
            'poster_url': movie.poster_url,
            'trailer_url': movie.trailer_url,
            'movie_status': movie.movie_status,
            'genres': list(genres),
            'showtimes': list(showtimes),
        })
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def get_movie_details(request, movie_id):
    """Get movie details by ID"""

    movie = get_object_or_404(Movie, pk=movie_id)
    genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
    showtimes = MovieShowtime.objects.filter(movie=movie).values_list('showtime_value', flat=True)

    data = {
        'movie_id': movie.movie_id,
        'movie_title': movie.movie_title,
        'movie_description': movie.movie_description,
        'age_rating': movie.age_rating,
        'poster_url': movie.poster_url,
        'trailer_url': movie.trailer_url,
        'movie_status': movie.movie_status,
        'genres': list(genres),
        'showtimes': list(showtimes), #[str(time) for time in showtimes]??
    }

    return JsonResponse(data)

@require_http_methods(["GET"])
def get_currently_running_movies(request):
    """Get movies that are currently showing"""
    movies = Movie.objects.filter(movie_status='Currently Running')
    data = []

    for movie in movies:
        genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
        showtimes = MovieShowtime.objects.filter(movie=movie).values_list('showtime_value', flat=True)
        data.append({
            'movie_id': movie.movie_id,
            'movie_title': movie.movie_title,
            'movie_description': movie.movie_description,
            'age_rating': movie.age_rating,
            'poster_url': movie.poster_url,
            'trailer_url': movie.trailer_url,
            'movie_status': movie.movie_status,
            'genres': list(genres),
            'showtimes': list(showtimes),
        })
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def get_coming_soon_movies(request):
    """Get movies that are coming soon"""
    movies = Movie.objects.filter(movie_status='Coming Soon')
    data = []

    for movie in movies:
        genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
        showtimes = MovieShowtime.objects.filter(movie=movie).values_list('showtime_value', flat=True)
        data.append({
            'movie_id': movie.movie_id,
            'movie_title': movie.movie_title,
            'movie_description': movie.movie_description,
            'age_rating': movie.age_rating,
            'poster_url': movie.poster_url,
            'trailer_url': movie.trailer_url,
            'movie_status': movie.movie_status,
            'genres': list(genres),
            'showtimes': list(showtimes),
        })
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def filter_movies_by_genre(request, genre_name):
    """Filter movies by genre"""
    try:
        #check if genre exists and get movies from that genre
        genre = Genre.objects.get(genre_name__iexact=genre_name)
        movies = Movie.objects.filter(moviegenre__genre=genre)
        data = []

        for movie in movies:
            genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
            #might not need showtimes, tbd
            # showtimes = MovieShowtime.objects.filter(movie=movie).values_list('showtime_value', flat=True)
            data.append({
                'movie_id': movie.movie_id,
                'movie_title': movie.movie_title,
                'movie_description': movie.movie_description,
                'age_rating': movie.age_rating,
                'poster_url': movie.poster_url,
                'trailer_url': movie.trailer_url,
                'movie_status': movie.movie_status,
                'genres': list(genres),
                # 'showtimes': list(showtimes),
            })
        return JsonResponse({
            'genre': genre_name,
            'count': len(data),
            'movies': data
        })
    
    except Genre.DoesNotExist:
        return JsonResponse({
            'error': f'Genre "{genre_name}" does not exist.'
        }, status=404)
    
@require_http_methods(["GET"])
def search_movies_by_name(request):
    """Search movies by name"""
    search_query = request.GET.get('q', '').strip()

    if not search_query:
        return JsonResponse({
            'error': 'Search query cannot be empty.'
        }, status=400)
    
    #searches for movies with titles containing the search, case insensitive
    movies = Movie.objects.filter(movie_title__icontains=search_query)
    data = []

    for movie in movies:
        genres = Genre.objects.filter(moviegenre__movie=movie).values_list('genre_name', flat=True)
        showtimes = MovieShowtime.objects.filter(movie=movie).values_list('showtime_value', flat=True)
        data.append({
            'movie_id': movie.movie_id,
            'movie_title': movie.movie_title,
            'movie_description': movie.movie_description,
            'age_rating': movie.age_rating,
            'poster_url': movie.poster_url,
            'trailer_url': movie.trailer_url,
            'movie_status': movie.movie_status,
            'genres': list(genres),
            'showtimes': list(showtimes),
        })
    return JsonResponse({
        'search_query': search_query,
        'count': len(data),
        'movies': data
    })
