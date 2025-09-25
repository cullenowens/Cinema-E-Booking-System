from django.db import models

# Create your models here.
 
 ## Example Models ##

class Movie(models.Model):
    title = models.CharField(max_length=200)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.title

class Theater(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name="showtimes")
    starts_at = models.DateTimeField()

    def __str__(self):
        return f"{self.movie.title} @ {self.starts_at:%Y-%m-%d %H:%M}"