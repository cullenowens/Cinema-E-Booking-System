from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet
import base64
from datetime import datetime

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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    subscribed = models.BooleanField(default=False)         # promotions
    status = models.CharField(max_length=10, default="Inactive")  # Active/Inactive
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_code_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile<{self.user.email}>"
    
class Promotion(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='promotions')
    movie_title = models.CharField(max_length=255)
    movie_description = models.TextField(blank=True, null=True)
    discount_percentage = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Promotion<{self.movie_title} - {self.discount_percentage}%>"
    


# uses the existing cinema_address table
class Address(models.Model):
    # each user has only one address (well at least in this model)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=50, blank=True, default='')
    state = models.CharField(max_length=50, blank=True, default='')
    zip_code = models.CharField(max_length=10, blank=True, default='')

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
        card_number = self.get_card_number()  # Get the real number
        if card_number and len(card_number) >= 4:
            return f"****-****-****-{card_number[-4:]}"  # Show last 4 digits
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
    
    def set_card_number(self, card_number):
        """encrypt and store card number"""
        try:
            cipher = Fernet(settings.CARD_ENCRYPTION_KEY.encode())
            encrypted_data = cipher.encrypt(card_number.encode())
            self.card_number_enc = base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")


    def get_card_number(self):
        """decrypt and return card number (for internal use only)"""
        if not self.card_number_enc:
            return None
        try:
            cipher = Fernet(settings.CARD_ENCRYPTION_KEY.encode())
            encrypted_data = base64.urlsafe_b64decode(self.card_number_enc.encode())
            return cipher.decrypt(encrypted_data).decode()
        except Exception:
            return None    