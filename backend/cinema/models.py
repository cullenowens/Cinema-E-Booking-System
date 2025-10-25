from django.conf import settings
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
        db_table = 'Genre_List'
        managed = False

    def __str__(self):
        return self.genre_name

class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Movie_Genres'
        managed = False # table already exists
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
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    subscribed = models.BooleanField(default=False)
    status = models.CharField(max_length=10, default="Inactive")

    class Meta:
        db_table = 'cinema_profile'  # Use existing table
        managed = True  # Django manages this table

    def __str__(self):
        return f"Profile<{self.user.email}>"


# uses the existing cinema_address table
class Address(models.Model):
    # each user has only one address (well at least in this model)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    class Meta:
        db_table = 'cinema_address'  # maps to the cinema_address table in the database
        managed = True  # django is managing this table

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"


# Use existing cinema_paymentcard table
class PaymentCard(models.Model):
    # each user can have multiple payment cards
    # added functionality to where if user gets deleted, their cards get deleted too
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    brand = models.CharField(max_length=20)  # Visa, MasterCard, etc.
    expiration = models.CharField(max_length=7)  # want it in MM/YYYY format
    card_number_enc = models.CharField(max_length=256)

    class Meta:
        db_table = 'cinema_paymentcard'  # maps to the cinema_paymentcard table
        managed = True  # django manages this table

    # this method is just to display the card info without exposing sensitive data
    def __str__(self):
        return f"{self.brand} - {self.expiration}"
    
    # just to look cool
    def get_masked_card_number(self):
        """Return masked card number for display"""
        return "****-****-****-****"

    # check if card is expired
    def is_expired(self):
        """Check if card is expired"""
        from datetime import datetime
        try:
            month, year = self.expiration.split('/')
            exp_date = datetime(int(year), int(month), 1)
            return exp_date < datetime.now()
        except:
            return True

        