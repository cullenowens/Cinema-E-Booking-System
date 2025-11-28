#this will map to existing tables in the database
#views will handle the logic and pull from the models created here
from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet
import base64

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
    
class Showroom(models.Model):
    """
    Model for movie showrooms/theaters
    Example:
    - Theater 1: 100 seats (Rows A-J, Seats 1-10)
    - Theater 2: 150 seats (Rows A-O, Seats 1-10)
    - Imax: 200 seats (Rows A-T, Seats 1-10)
    """
    showroom_id = models.AutoField(primary_key=True)

    showroom_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'showrooms'
        managed = False

    def __str__(self):
        return self.showroom_name

class Seat(models.Model):
    """
    Represents individual seats in a showroom

    Example seats in Theater 1:
    - seat_id: 1, showroom_id: 1, row_label = 'A', seat_number = 1
    - seat_id: 2, showroom_id: 1, row_label = 'A', seat_number = 2
    - seat_id: 3, showroom_id: 1, row_label = 'A', seat_number = 3

    Table used to track seat availability for showings, show seat map, and prevent double bookings
    """
    seat_id = models.AutoField(primary_key=True)

    showroom_id = models.ForeignKey(

        Showroom,
        # crucial to note that if showroom is deleted, all its seats are deleted too
        # seats are meaningless without a showroom
        on_delete=models.CASCADE,
        db_column='showroom_id',
        # added so we can access seats from showroom instance (Access via showroom.seats.all())
        related_name='seats'
    )

    row_label = models.CharField(max_length=1)
    seat_number = models.PositiveIntegerField()

    class Meta:
        db_table = 'seats'
        managed = False
        # ensure unique seat per showroom
        unique_together = ('showroom_id', 'row_label', 'seat_number')
        # adding so seats return sorted by row and number (A1, A2, A3...B1, B2, B3...)
        ordering = ['row_label', 'seat_number']
        
    def __str__(self):
        return f"{self.row_label}{self.seat_number}"


class Showing(models.Model):
    """Model for movie showings (scheduled screenings)"""
    showing_id = models.AutoField(primary_key=True)

    movie = models.ForeignKey(
        Movie,
        # delete showings if movie is deleted
        on_delete=models.CASCADE,
        db_column='movie_id',
        # added so we can access showings from movie instance (Access via movie.showings.all())
        related_name='showings'
    )
    
    showroom = models.ForeignKey(
        Showroom,
        on_delete=models.CASCADE,
        db_column='showroom_id',
        # added so we can access showings from showroom instance (Access via showroom.showings.all())
        related_name='showings'
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'showings'
        managed = False
        unique_together = ('showroom', 'start_time')
        # add ordering by start time
        ordering = ['start_time']

    def __str__(self):
        return f"{self.movie.movie_title} - {self.showroom.showroom_name} - {self.start_time.strftime('%b %d, %I:%M %p')}"    


class Booking(models.Model):
    """
    Represents a user's booking for a specific showing
    """
    booking_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='user_id',
        # added so we can access bookings from user instance (Access via user.bookings.all())
        related_name='bookings'
    )

    class Meta:
        db_table = 'bookings'
        managed = False

    def __str__(self):
        return f"Booking #{self.booking_id} by {self.user.username}"
    
class Ticket(models.Model):
    """
    Represents one ticket within a booking
    """

    AGE_CATEGORIES = [
        ('Child', 'Child'),
        ('Adult', 'Adult'),
        ('Senior', 'Senior'),
    ]

    # each ticket is linked to a booking
    ticket_id = models.AutoField(primary_key=True)

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        db_column='booking_id',
        # added so we can access tickets from booking instance (Access via booking.tickets.all())
        related_name='tickets'
    )

    showing = models.ForeignKey(
        Showing,
        on_delete=models.CASCADE,
        db_column='showing_id',
        # added so we can access tickets from showing instance (Access via showing.tickets.all())
        related_name='tickets'
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        db_column='seat_id',
        related_name='tickets'
    )
    
    age_category = models.CharField(
        max_length=10,
        choices=AGE_CATEGORIES
    )

    class Meta:
        db_table = 'tickets'
        managed = False

    def __str__(self):
        return f"Ticket #{self.ticket_id} - Seat {self.seat} - {self.age_category}"
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True)
    subscribed = models.BooleanField(default=False)         # promotions
    status = models.CharField(max_length=10, default="Inactive")  # Active/Inactive
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_code_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile<{self.user.email}>"
    
class Promotion(models.Model):
    promo_id = models.AutoField(primary_key=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    promo_code = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    #is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cinema_promotions'
        managed = False

    def __str__(self):
        return f"Promotion<{self.promo_code} - {self.discount}%>"
    


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