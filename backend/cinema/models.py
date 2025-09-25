from django.db import models

class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=255)
    movie_description = models.TextField(blank=True, null=True)
    age_rating = models.CharField(max_length=10, blank=True, null=True)
    poster_url = models.CharField(max_length=255, blank=True, null=True)
    trailer_url = models.CharField(max_length=255, blank=True, null=True)
    movie_status = models.CharField(
        max_length=50,
        choices=[
            ('Currently Running', 'Currently Running'),
            ('Coming Soon', 'Coming Soon')
        ],
        default='Coming Soon'
    )

    class Meta:
        db_table = 'Movies'
        managed = False  # Since the table already exists in the database

    def __str__(self):
        return self.movie_title
    
class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'Genres'
        managed = False

    def __str__(self):
        return self.genre_name

class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Movie_Genres'
        unique_together = ('movie', 'genre')

class MovieShowtime(models.Model):
    showtime_id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='movie_id')
    showtime_value = models.TimeField()

    class Meta:
        db_table = 'Movie_Showtimes'
        managed = False

    def __str__(self):
        return f"{self.movie.movie_title} - {self.showtime_value}"