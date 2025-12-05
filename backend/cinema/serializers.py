#takes an object from the database (eg Movie) and converts it to JSON for API responses
#or, takes info from frontend (password= serializers...), validates fields, then creates/updates database objects
from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db import models
import logging
from .models import (
    Profile, Movie, Promotion, PaymentCard, Address, Genre, MovieGenre, 
    Showing, Showroom, Seat, Booking, Ticket
)

# --- Movie Serializer ---
# Handles Movie model serialization (for display or creation)

class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for Movie model with complete validation
    Handles movie creation with genres
    """
    # Accept genres as a list of genre names or IDs
    genres = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=True,
        help_text="List of genre names (e.g., ['Action', 'Comedy'])"
    )
    
    class Meta:
        model = Movie
        fields = [
            'movie_id', 
            'movie_title', 
            'movie_description', 
            'age_rating', 
            'poster_url', 
            'trailer_url', 
            'movie_status',
            'genres'
        ]
        read_only_fields = ['movie_id']
    
    def validate_movie_title(self, value):
        """Ensure movie title is not empty and is unique"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("Movie title cannot be empty")
        
        # Check for duplicate titles (case-insensitive)
        if Movie.objects.filter(movie_title__iexact=value).exists():
            # If updating, allow same title for same movie
            if self.instance and self.instance.movie_title.lower() == value.lower():
                return value
            raise serializers.ValidationError("A movie with this title already exists")
        
        return value.strip()
    
    def validate_movie_description(self, value):
        """Ensure description is provided and has minimum length"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("Movie description is required")
        
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Movie description must be at least 10 characters")
        
        return value.strip()
    
    def validate_age_rating(self, value):
        """Validate age rating is one of the standard ratings"""
        valid_ratings = ['G', 'PG', 'PG-13', 'R', 'NC-17', 'NR']
        
        if not value or value.strip() == "":
            raise serializers.ValidationError("Age rating is required")
        
        value = value.strip().upper()
        
        if value not in valid_ratings:
            raise serializers.ValidationError(
                f"Age rating must be one of: {', '.join(valid_ratings)}"
            )
        
        return value
    
    def validate_poster_url(self, value):
        """Validate poster URL is provided"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("Poster URL is required")
        
        # Basic URL validation
        if not (value.startswith('http://') or value.startswith('https://')):
            raise serializers.ValidationError("Poster URL must be a valid URL starting with http:// or https://")
        
        return value.strip()
    
    def validate_trailer_url(self, value):
        """Validate trailer URL is provided"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("Trailer URL is required")
        
        # Basic URL validation
        if not (value.startswith('http://') or value.startswith('https://')):
            raise serializers.ValidationError("Trailer URL must be a valid URL starting with http:// or https://")
        
        return value.strip()
    
    def validate_movie_status(self, value):
        """Validate movie status is valid"""
        valid_statuses = ['Currently Running', 'Coming Soon']
        
        if not value:
            raise serializers.ValidationError("Movie status is required")
        
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Movie status must be one of: {', '.join(valid_statuses)}"
            )
        
        return value
    
    def validate_genres(self, value):
        """Validate that at least one genre is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one genre is required")
        
        # Check that all genres exist in the database
        for genre_name in value:
            if not Genre.objects.filter(genre_name__iexact=genre_name).exists():
                raise serializers.ValidationError(
                    f"Genre '{genre_name}' does not exist. Please use valid genre names."
                )
        
        return value
    
    def create(self, validated_data):
        """Create movie with genres"""
        # Extract genres from validated data
        genres = validated_data.pop('genres', [])
        
        # Create the movie
        movie = Movie.objects.create(**validated_data)
        
        # Add genres to the movie
        for genre_name in genres:
            genre = Genre.objects.get(genre_name__iexact=genre_name)
            MovieGenre.objects.create(movie=movie, genre=genre)
        
        return movie
    
    def update(self, instance, validated_data):
        """Update movie and its genres"""
        # Extract genres if provided
        genres = validated_data.pop('genres', None)
        
        # Update movie fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update genres if provided
        if genres is not None:
            # Remove existing genre associations
            MovieGenre.objects.filter(movie=instance).delete()
            
            # Add new genres
            for genre_name in genres:
                genre = Genre.objects.get(genre_name__iexact=genre_name)
                MovieGenre.objects.create(movie=instance, genre=genre)
        
        return instance
    
class ShowroomSerializer(serializers.ModelSerializer):
    """Serializer for Showroom model"""
    
    class Meta:
        model = Showroom
        fields = ['showroom_id', 'showroom_name']
        read_only_fields = ['showroom_id']


class ShowingSerializer(serializers.ModelSerializer):
    """
    Serializer for Showing model with conflict detection
    """
    movie_id = serializers.IntegerField(write_only=True)
    showroom_id = serializers.IntegerField(write_only=True)
    
    # Read-only fields for display
    movie_title = serializers.CharField(source='movie.movie_title', read_only=True)
    showroom_name = serializers.CharField(source='showroom.showroom_name', read_only=True)
    
    class Meta:
        model = Showing
        fields = [
            'showing_id',
            'movie_id',
            'movie_title',
            'showroom_id', 
            'showroom_name',
            'start_time',
            'end_time'
        ]
        read_only_fields = ['showing_id']
    
    def validate_movie_id(self, value):
        """Validate that movie exists"""
        if not Movie.objects.filter(movie_id=value).exists():
            raise serializers.ValidationError(f"Movie with ID {value} does not exist")
        return value
    
    def validate_showroom_id(self, value):
        """Validate that showroom exists"""
        if not Showroom.objects.filter(showroom_id=value).exists():
            raise serializers.ValidationError(f"Showroom with ID {value} does not exist")
        return value
    
    def validate_start_time(self, value):
        """Validate that start time is in the future"""
        if value < timezone.now():
            raise serializers.ValidationError("Start time must be in the future")
        return value
    
    def validate(self, data):
        """
        Validate that there are no scheduling conflicts
        Check if the showroom is available at the requested time
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        showroom_id = data.get('showroom_id')
        
        # If end_time not provided, estimate it (assume 2.5 hour movie)
        if not end_time:
            end_time = start_time + timedelta(hours=2, minutes=30)
            data['end_time'] = end_time
        
        # Validate end_time is after start_time
        if end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time"
            })
        
        # Check for conflicts in the same showroom
        # A conflict exists if:
        # 1. Another showing starts during this showing
        # 2. This showing starts during another showing
        # 3. Showings overlap in any way
        
        conflicts = Showing.objects.filter(
            showroom_id=showroom_id
        ).filter(
            models.Q(
                # Case 1: New showing starts during existing showing
                start_time__lt=end_time,
                end_time__gt=start_time
            ) | models.Q(
                # Case 2: Existing showing starts during new showing
                start_time__gte=start_time,
                start_time__lt=end_time
            )
        )
        
        # Exclude current instance if updating
        if self.instance:
            conflicts = conflicts.exclude(showing_id=self.instance.showing_id)
        
        if conflicts.exists():
            conflict = conflicts.first()
            raise serializers.ValidationError({
                "conflict": f"Showroom '{conflict.showroom.showroom_name}' is already booked for '{conflict.movie.movie_title}' from {conflict.start_time.strftime('%Y-%m-%d %I:%M %p')} to {conflict.end_time.strftime('%I:%M %p')}"
            })
        
        return data
    
    def create(self, validated_data):
        """Create showing with movie and showroom"""
        movie_id = validated_data.pop('movie_id')
        showroom_id = validated_data.pop('showroom_id')
        
        movie = Movie.objects.get(movie_id=movie_id)
        showroom = Showroom.objects.get(showroom_id=showroom_id)
        
        showing = Showing.objects.create(
            movie=movie,
            showroom=showroom,
            **validated_data
        )
        
        return showing
    
    def update(self, instance, validated_data):
        """Update showing"""
        movie_id = validated_data.pop('movie_id', None)
        showroom_id = validated_data.pop('showroom_id', None)
        
        if movie_id:
            instance.movie = Movie.objects.get(movie_id=movie_id)
        if showroom_id:
            instance.showroom = Showroom.objects.get(showroom_id=showroom_id)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

# --- Promotion Serializer ---
# handles promotion data with discount_type and discount_value fields

class PromotionSerializer(serializers.ModelSerializer):
    """serializer for promotions using discount_type and discount_value"""
    class Meta:
        model = Promotion
        fields = ['promo_id', 'promo_code', 'discount_type', 'discount_value', 'start_date', 'end_date', 'created_at']
        read_only_fields = ['promo_id', 'created_at']

    def validate_promo_code(self, value):
        """make sure promo code is unique and formatted correctly"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("promo code cannot be empty")
        
        value = value.strip().upper()
        
        if len(value) < 3:
            raise serializers.ValidationError("promo code must be at least 3 characters")
        
        import re
        if not re.match(r'^[A-Z0-9_-]+$', value):
            raise serializers.ValidationError("promo code can only contain letters, numbers, hyphens, and underscores")
        
        if Promotion.objects.filter(promo_code__iexact=value).exists():
            if self.instance and self.instance.promo_code.upper() == value:
                return value
            raise serializers.ValidationError("a promotion with this code already exists")
        
        return value
    
    def validate_discount_type(self, value):
        """check discount type is either percentage or fixed"""
        if not value:
            raise serializers.ValidationError("discount type is required")
        
        valid_types = ['percentage', 'fixed']
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"discount type must be one of: {', '.join(valid_types)}")
        
        return value.lower()
    
    def validate_discount_value(self, value):
        """make sure discount value is positive"""
        if value is None:
            raise serializers.ValidationError("discount value is required")
        
        if value <= 0:
            raise serializers.ValidationError("discount value must be greater than 0")
        
        return value
    
    def validate_start_date(self, value):
        """check start date is today or future"""
        if not value:
            raise serializers.ValidationError("start date is required")
        
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("start date cannot be in the past")
        
        return value
    
    def validate_end_date(self, value):
        """check end date exists"""
        if not value:
            raise serializers.ValidationError("end date is required")
        
        return value
    
    def validate(self, data):
        """cross-field validation for discount type and dates"""
        discount_type = data.get('discount_type')
        discount_value = data.get('discount_value')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # percentage discounts cant exceed 100%
        if discount_type == 'percentage' and discount_value > 100:
            raise serializers.ValidationError({"discount_value": "percentage discount cannot exceed 100%"})
        
        # end date must be after start date
        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({"end_date": "end date must be after start date"})
        
        return data

# --- User Registration Serializer ---
# Creates new users and associated profiles

class RegisterSerializer(serializers.ModelSerializer):
    #receives data from frontend for registration and validates it
    password = serializers.CharField(write_only=True)
    subscribed = serializers.BooleanField(write_only=True, required=False, default=False)
    phone = serializers.CharField(required=True, write_only=True)


    class Meta:
        model = User #creating user model
        fields = ["username", "email", "phone", "password", "subscribed"]

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use")
        return value
    
    def validate_phone(self, value):
        """Phone validation"""
        phone_digits = ''.join(filter(str.isdigit, value))
        if len(phone_digits) < 10:
            raise serializers.ValidationError("Phone number must have at least 10 digits")
        return value

# Creates user and inactive profile (activated later)
    def create(self, validated_data):
        subscribed = validated_data.pop("subscribed", False)
        phone = validated_data.pop("phone")
        #create user (in auth_user table)
        user = User.objects.create_user(**validated_data)
        #create associated profile (in cinema_profile table)
        Profile.objects.create(user=user, phone=phone, subscribed=subscribed, status="Inactive")
        #creates empty address for the user
        Address.objects.create(
            user=user,
            street="",
            city="",
            state="",
            zip_code=""
        )
        return user
    
# --- Admin Registration Serializer ---
# Creates staff (admin) users with active profiles

class AdminRegisterSerializer(serializers.ModelSerializer):
    #for crearting admin users
    #could look into hardcoding admin users
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

# Creates admin user and marks them active
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_staff = True
        user.save()
        Profile.objects.create(user=user, status="Active", subscribed=True)
        return user

# --- Login Serializer ---
# Handles login credentials and optional remember-me flag

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(required=False, default=False)

# --- Profile Serializer ---
# Serializes user profile details

class ProfileSerializer(serializers.ModelSerializer):
    #user fields
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name', required= False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    #profile fields
    phone = serializers.CharField(required=False, allow_blank=True)
    subscribed = serializers.BooleanField()
    status = serializers.CharField(read_only=True)

     #update user and profile fields
    class Meta:
        model = Profile
        fields = ["username", "email", "first_name", "last_name", "phone", "subscribed", "status"]

    def update(self, instance, validated_data):
        #update user fields
        user_data = validated_data.pop('user', {})
        user = instance.user
        #update user model fields
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.save()
        #update profile fields
        instance.phone = validated_data.get('phone', instance.phone)
        instance.subscribed = validated_data.get('subscribed', instance.subscribed)
        instance.save()
        return instance


# --- Address Serializer ---
# Serializes user addresses and auto-links them to the current user

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'zip_code']

    def create(self, validated_data):
        # automatically assign current user to the address
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# --- Payment Card Serializer ---
# Serializes payment card data securely (encrypts number)

class PaymentCardSerializer(serializers.ModelSerializer):
    # stores the encrypted card number
    masked_card_number = serializers.SerializerMethodField(read_only=True)
    # checks if card is expired
    is_expired = serializers.SerializerMethodField(read_only=True)

    # field that receives the card number from frontend(made it write only for security and 19 max length for format)
    card_number = serializers.CharField(write_only=True, max_length=19)

    class Meta:
        model = PaymentCard
        fields = ['id', 'brand', 'expiration', 'card_number', 'masked_card_number', 'is_expired']
        extra_kwargs = {
            'card_number_enc': {'write_only': True},
        }

    # getter method to return masked card number
    def get_masked_card_number(self, obj):
        """Return masked card number for safe/cool display"""
        return obj.get_masked_card_number()

    # getter method to check if card is expired
    def get_is_expired(self, obj):
        """Check if card is expired"""
        return obj.is_expired()
    
    # method to validate card number format and return cleaned number
    def validate_card_number(self, value):
        """validate card number format before encryption"""
        # remove spaces, dashes, and other non-digit characters
        card_number = ''.join(filter(str.isdigit, value))
    
        # check if we have any digits left
        if not card_number:
            raise serializers.ValidationError("Card number must contain digits")
    
        # check length (most cards are 13-19 digits)
        if len(card_number) < 13 or len(card_number) > 19:
            raise serializers.ValidationError("Card number must be between 13 and 19 digits")
    
        return card_number
    
    # method to validate expiration date format MM/YYYY and check if expired
    def validate_expiration(self, value):
        """Validate expiration date format MM/YYYY"""
        try:
            # check format to see if it is MM/YYYY
            if '/' not in value or len(value) != 7:
                raise serializers.ValidationError("Expiration must be in MM/YYYY format")
        
            month, year = value.split('/')
            month = int(month)
            year = int(year)
        
            # check month range 01-12
            if month < 1 or month > 12:
                raise serializers.ValidationError("Month must be between 01 and 12")
        
            # check if card is already expired
            from datetime import datetime
            current_year = datetime.now().year
            current_month = datetime.now().month
        
            if year < current_year or (year == current_year and month < current_month):
                raise serializers.ValidationError("Card cannot be expired")
            
            return value
        except ValueError:
            raise serializers.ValidationError("Expiration must be in MM/YYYY format")
    
    # method to create PaymentCard instance with encrypted card number
    def create(self, validated_data):
        """create payment card with REAL encryption"""
        # extract card number before creating the card
        card_number = validated_data.pop('card_number')
    
        # add user from request context
        validated_data['user'] = self.context['request'].user
    
        # create card with other fields (user, brand, expiration)
        card = PaymentCard.objects.create(**validated_data)
    
        # uses the model method to set encrypted card number
        card.set_card_number(card_number)
        card.save()
    
        return card
    
    # method to update PaymentCard instance (no card number changes allowed for security)
    def update(self, instance, validated_data):
        """Update card info (no card number changes for security)"""
        # removes card_number if someone tries to update it
        validated_data.pop('card_number', None)
        # updates other fields using parent update method
        return super().update(instance, validated_data)
    
class UserDetailSerializer(serializers.ModelSerializer):
    #user for displaying user info
    #read-only!!
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone = serializers.CharField()
    subscribed = serializers.BooleanField()
    status = serializers.CharField(read_only=True)
    class Meta:
        model = Profile
        fields = ["username", "email", "first_name", "last_name", "phone", "subscribed", "status"]


# --- User Portal Serializers ---

class SeatSerializer(serializers.ModelSerializer):
    """
    Basic seat serializer for displaying seat info.

    Purpose is to show seat details in API responses (used for admin, generic lists)

    Example output:
    {
        "seat_id": 1,
        "row_label": "A",
        "seat_number": 1,
        "seat_display": "A1"
    }
    """
    seat_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Seat
        fields = ['seat_id', 'row_label', 'seat_number', 'seat_display']
        read_only_fields = ['seat_id']

    def get_seat_display(self, obj):
        """Display seat as 'A1', 'B5', etc."""
        return f"{obj.row_label}{obj.seat_number}"
    

class SeatAvailabilitySerializer(serializers.ModelSerializer):
    """
    Seat serializer WITH availability status for a specific showing.
    shows which seats are available vs. booked for seating selection.

    Example output:
    {
        "seat_id": 1,
        "row_label": "A",
        "seat_number": 1,
        "seat_display": "A1",
        "is_available": true,
        "ticket_type": null
    }

    Key feature = is_available dynamically checks if seat is booked for specific showing.
    """
    # variables to hold showing context
    seat_display = serializers.SerializerMethodField(read_only=True)
    is_available = serializers.SerializerMethodField(read_only=True)
    ticket_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Seat
        fields = [
            'seat_id',
            'row_label',
            'seat_number',
            'seat_display',
            'is_available',
            'ticket_type'
        ]
        read_only_fields = ['seat_id']

    def get_seat_display(self, obj):
        '''Display seat as 'A1', 'B5', etc.'''
        return f"{obj.row_label}{obj.seat_number}"
    
    # method to check if seat is available for the given showing
    def get_is_available(self, obj):
        '''
        Check if seat is available for the given showing.

        requires showing_id in context from view.
        serializer = SeatAvailabilitySerializer(seats, many=True, context={'showing_id': 42})
        '''
        showing_id = self.context.get('showing_id')

        if not showing_id:
            # if no showing_id provided, assume the seat is available
            return True

        # check if a ticket exists for this seat + showing combo
        return not Ticket.objects.filter(
            showing_id=showing_id,
            seat=obj
        ).exists()
    
    # method to check ticket type if seat is booked
    def get_ticket_type(self, obj):
        '''
        if the seat is booked, return the ticket type (Adult, Child, Senior).
        if available, return None.
        '''
        showing_id = self.context.get('showing_id')

        if not showing_id:
            return None
        
        try:
            ticket = Ticket.objects.get(
                showing_id=showing_id,
                seat=obj
            )
            return ticket.age_category
        except Ticket.DoesNotExist:
            return None
        

class ShowingDetailSerializer(serializers.ModelSerializer):
    '''
    Detailed showing serializer for User portal (includes availability).

    shows complete showing info + seat availability for user booking
    different from the ShowingSerializer used for admin scheduling and operations.

    Example output:
    {
        "showing_id": 42,
        "movie_id": 5,
        "movie_title": "Inception",
        "movie_poster": "https://...",
        "showroom_id": 1,
        "showroom_name": "Theater 1",
        "start_time": "2025-11-15T19:30:00Z",
        "end_time": "2025-11-15T22:00:00Z",
        "available_seats": 95,
        "total_seats": 100
    }
    '''
    # variables for detailed display
    movie_title = serializers.CharField(source='movie.movie_title', read_only=True)
    movie_poster = serializers.CharField(source='movie.poster_url', read_only=True)
    showroom_name = serializers.CharField(source='showroom.showroom_name', read_only=True)
    available_seats = serializers.SerializerMethodField(read_only=True)
    total_seats = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Showing
        fields = [
            'showing_id',
            'movie_id',
            'movie_title',
            'movie_poster',
            'showroom_id',
            'showroom_name',
            'start_time',
            'end_time',
            'available_seats',
            'total_seats'
        ]
        read_only_fields = ['showing_id']

    def get_total_seats(self, obj):
        '''Count total seats in the showroom'''
        return obj.showroom.seats.count()
        
    def get_available_seats(self, obj):
        '''calculates the available seats for this showing'''
        total_seats = obj.showroom.seats.count()
        booked_seats = Ticket.objects.filter(showing=obj).count()
        return total_seats - booked_seats
        

class SeatMapSerializer(serializers.Serializer):
    '''
    Serializer for complete seat map with availability for a showing.

    generates the entire seat layout for showing's booking page.

    Example output:
    {
        "showing": {
            "showing_id": 42,
            "movie_title": "Inception",
            ...
        },
        "seats_by_row": {
            "A": [
                {"seat_id": 1, "seat_number": 1, "is_available": true},
                {"seat_id": 2, "seat_number": 2, "is_available": false},
                ...
            ],
            "B": [...],
            ...
        },
        "total_seats": 100,
        "available_seats": 95
    }
    '''

    showing = ShowingDetailSerializer(read_only=True)
    seats_by_row = serializers.SerializerMethodField(read_only=True)
    total_seats = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    def get_seats_by_row(self, obj):
        '''
        Group seats by row for frontend display.
        Returns: {"A": [seats], "B": [seats], ...}
        '''
        from collections import defaultdict

        showing = obj['showing']
        seats = obj['seats']

        # groups seats by row
        seats_by_row = defaultdict(list)

        for seat in seats:
            seat_data = SeatAvailabilitySerializer(
                seat,
                context={'showing_id': showing.showing_id}
            ).data
            seats_by_row[seat.row_label].append(seat_data)
        
        # convert to regular dict and sort rows alphabetically
        return dict(sorted(seats_by_row.items()))
    

class TicketSerializer(serializers.ModelSerializer):
    '''
    Serializer for individual tickets.

    purpose is to display ticket details in bookings.

    Example output:
    {
        "ticket_id": 456,
        "seat_id": 5,
        "seat_display": "A5",
        "age_category": "Adult",
        "price": 12.00
    }
    '''
    seat_display = serializers.CharField(source='seat.__str__', read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'ticket_id',
            'seat_id',
            'seat_display',
            'age_category',
            'price'
        ]
        read_only_fields = ['ticket_id']

    def get_price(self, obj):
        '''
        calculate ticket price based on age category.

        Pricing:
        - Child: $8.00
        - Adult: $12.00
        - Senior: $10.00
        '''
        pricing = {
            'Child': 8.00,
            'Adult': 12.00,
            'Senior': 10.00
        }
        # default to Adult price if category not found
        return pricing.get(obj.age_category, 12.00)
    
class BookingCreateSerializer(serializers.Serializer):
    '''
    serializer for creating a new booking including the checkout process
    
    purpose is to handle user's seat selection and create booking + tickets

    example input:
    {
        "showing_id": 42, 
        "seats": [
            {"seat_id": 5, "age_category": "Adult"},
            {"seat_id": 6, "age_category": "Child"},
            {"seat_id": 7, "age_category": "Senior"}
        ],
        "promo_code": "SUMMER20",  # Optional
        "payment_card_id": 3,  # Use saved card
        # OR provide new card:
        "card_number": "4532123456789012",
        "expiration": "12/2026",
        "brand": "Visa"
    }
    '''

    showing_id = serializers.IntegerField(required=True)
    seats = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=10,
        required=True
    )

    # optional promotion code
    promo_code = serializers.CharField(required=False, allow_blank=True)

    # payment: either saved card OR new card info
    payment_card_id = serializers.IntegerField(required=False)
    card_number = serializers.CharField(required=False, max_length=19)
    expiration = serializers.CharField(required=False, max_length=7)  # MM/YYYY
    brand = serializers.CharField(required=False, max_length=50)


    def validate(self, data):
        """
        check either saved or new card and validate
        """
        payment_card_id = data.get('payment_card_id')
        card_number = data.get('card_number')
        
        # must provide either a saved card ID or new card info
        if not payment_card_id and not card_number:
            raise serializers.ValidationError({
                "payment": "Payment information is required. Provide either payment_card_id or new card details."
            })
        
        # if providing new card, all card fields are required
        if card_number:
            required_fields = ['expiration', 'brand']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f"{field} is required when providing new card information"
                    })
                
        # validate seats structure
        seats_data = data.get('seats', [])
        for seat_data in seats_data:
            if 'seat_id' not in seat_data:
                raise serializers.ValidationError({
                    "seats": "Each seat must have a seat_id"
                })
            if 'age_category' not in seat_data:
                raise serializers.ValidationError({
                    "seats": "Each seat must have an age_category (Child, Adult, or Senior)"
                })
        
        return data
    
    def create(self, validated_data):
        """
        makes booking using the facade pattern to simplify complex process.
        
        The Facade takes care of:
        seat validation
        price calculation
        promotion application (Factory Method)
        payment simulation
        booking and ticket creation
        
        Returns:
            dict: Complete booking result with all details
        """
        user = self.context['request'].user
        
        # extract data
        showing_id = validated_data['showing_id']
        seats_data = validated_data['seats']
        promo_code = validated_data.get('promo_code', '').strip()

        # build payment info dict
        payment_info = {}
        if validated_data.get('payment_card_id'):
            payment_info['payment_card_id'] = validated_data['payment_card_id']
        else:
            payment_info['card_number'] = validated_data.get('card_number')
            payment_info['expiration'] = validated_data.get('expiration')
            payment_info['brand'] = validated_data.get('brand')
        
        # use Facade to process the entire booking
        facade = BookingFacade(
            user=user,
            showing_id=showing_id,
            seats_data=seats_data,
            promo_code=promo_code if promo_code else None,
            payment_info=payment_info
        )
        
        # process booking and return result
        # the Facade handles all validation, calculation, and creation
        return facade.process_booking()

class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for viewing booking history.
    
    Purpose: Show user their bookings with full details including promotions and payment.
    
    Example output:
    {
        "booking_id": 123,
        "booking_time": "2025-12-03T10:30:00Z",
        "user_email": "john@email.com",
        "movie_title": "Inception",
        "showroom_name": "Theater 1",
        "start_time": "2025-11-15T19:30:00Z",
        "tickets": [
            {"seat_display": "A5", "age_category": "Adult", "price": 12.00},
            {"seat_display": "A6", "age_category": "Child", "price": 8.00}
        ],
        "total_price": 20.00
    }
    """

    user_email = serializers.EmailField(source='user.email', read_only=True)
    movie_title = serializers.CharField(
        source='tickets.first.showing.movie.movie_title',
        read_only=True
    )
    showroom_name = serializers.CharField(
        source='tickets.first.showing.showroom.showroom_name',
        read_only=True
    )
    start_time = serializers.DateTimeField(
        source='tickets.first.showing.start_time',
        read_only=True
    )
    tickets = TicketSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'booking_time',
            'user_email',
            'movie_title',
            'showroom_name',
            'start_time',
            'tickets',
            'total_price'
        ]
        read_only_fields = ['booking_id', 'booking_time']
    
    def get_total_price(self, obj):
        """Calculate total price for all tickets."""
        pricing = {
            'Child': 8.00,
            'Adult': 12.00,
            'Senior': 10.00
        }
        
        total = sum(
            pricing.get(ticket.age_category, 12.00)
            for ticket in obj.tickets.all()
        )
        
        return total
    

# --- Factory Method pattern --- #
# adding this to handle different promotion types
# Allows for easy extension of new promotion types without modifying existing code

class PromotionFactory:
    """
    factory class is used to create appropriate promotion handler based on promo code.
    
    Design Pattern: Factory Method
    Purpose: Encapsulate promotion logic and allow easy addition of new promotion types.
    
    Returns appropriate promotion handler (Percentage, Fixed, or No promotion).
    """
    @staticmethod
    def get_promotion(promo_code):
        '''
        creates and returns the appropriate promotion handler based on promo_code.

        Args:
            promo_code (str): The promo code entered by the user.

        Returns:
            An instance of a promotion handler (PercentagePromotion, FixedPromotion, NoPromotion).
        '''
        if not promo_code:
            return NoPromotion()
        
        try:
            # query the Promotion model
            promo = Promotion.objects.get(promo_code__iexact=promo_code)

            # checking if it is valid at the moment
            from datetime import date
            today = date.today()
            if promo.start_date > today:
                return ExpiredPromotion(promo, 'Promotion has not started yet.')
            if promo.end_date < today:
                return ExpiredPromotion(promo, 'Promotion has expired.')
            
            # check discount type to decide which handler to use
            if promo.discount_type == 'percentage':
                return PercentagePromotion(promo)
            else:
                return FixedPromotion(promo)
            
        except Promotion.DoesNotExist:
            return InvalidPromotion()


class PercentagePromotion:
    """
    handles percentage-based promotions like 20% off
    discount_value stores the percentage as a whole number (20.00 = 20%)
    """
    def __init__(self, promo):
        self.promo = promo
        self.promo_code = promo.promo_code
        self.discount_value = float(promo.discount_value)
    
    def apply(self, total_price: float) -> float:
        """apply percentage discount to total, cant go below 0"""
        discount_amount = (self.discount_value / 100) * total_price
        final_price = total_price - discount_amount
        return round(max(0, final_price), 2)

    def get_discount_display(self, base_price: float) -> str:
        """show discount as percentage with dollar amount"""
        discount_amount = (self.discount_value / 100) * base_price
        return f"{self.discount_value:.0f}% off (-${discount_amount:.2f})"
    
    def is_valid(self):
        """check if promo is still valid"""
        return True
class FixedPromotion:
    """
    handles fixed dollar amount promotions like $10 off
    discount_value stores the dollar amount to subtract
    """
    def __init__(self, promo):
        self.promo = promo
        self.promo_code = promo.promo_code
        self.discount_value = float(promo.discount_value)
    
    def apply(self, total):
        """subtract fixed amount from total, cant go below 0"""
        return round(max(0, total - self.discount_value), 2)
    
    def get_discount_display(self, total):
        """show discount as dollar amount"""
        discount_amount = min(self.discount_value, total)
        return f"${discount_amount:.2f} off"
    
    def is_valid(self):
        """check if promo is still valid"""
        return True
    
class NoPromotion:
    """handles when there is no promotion is applied"""
    def __init__(self):
        self.promo_code = None
    
    def apply(self, total):
        """no discount applied"""
        return total
    
    def get_discount_display(self, total):
        """no discount to display"""
        return "No promotion applied"
    
    def is_valid(self):
        return True
    
class InvalidPromotion:
    """handler for invalid promo codes"""
    def __init__(self):
        self.promo_code = None
        self.error = "Invalid promo code"
    
    def apply(self, total):
        """no discount applied"""
        return total
    
    def get_discount_display(self, total):
        """return error message"""
        return self.error
    
    def is_valid(self):
        """invalid promotion"""
        return False
    
class ExpiredPromotion:
    """handler for expired or not-yet-started promo codes"""
    def __init__(self, promo, error_message):
        self.promo = promo
        self.promo_code = promo.promo_code
        self.error = error_message
    
    def apply(self, total):
        """no discount applied"""
        return total
    
    def get_discount_display(self, total):
        """return error message"""
        return self.error
    
    def is_valid(self):
        """expired/invalid promotion"""
        return False
    

# --- Facade Pattern --- #
# this coordinates booking process
# makes a single interface

class BookingFacade:
    '''
    Coordinates the booking process for users.

    Design Pattern: Facade
    Provides a simple interface to complex booking operations.
    
    Handles:
    - Validating seats and showing
    - Calculating total price
    - Applying promotions (via Factory Method)
    - Processing payment
    - Creating booking and tickets
    '''

    def __init__(self, user, showing_id, seats_data, promo_code=None, payment_info=None):
        """
        Initialize the booking facade with input data
        
        Args:
            user: The authenticated user making the booking
            showing_id: ID of the showing to book
            seats_data: List of dicts with seat_id and age_category
            promo_code: Optional promotion code
            payment_info: Dict with payment card info or payment_card_id
        """
        self.user = user
        self.showing_id = showing_id
        self.seats_data = seats_data
        self.promo_code = promo_code
        self.payment_info = payment_info or {}
        
        # Initialize attributes that will be set during processing
        self.showing = None
        self.seats = []
        self.promotion = None
        self.base_price = 0.0
        self.final_price = 0.0
        self.booking = None
        self.tickets = []

    def process_booking(self):
        """
        Main method to process the entire booking flow
        
        Returns:
            dict: Booking result with all details
        
        Raises:
            serializers.ValidationError: If any step fails
        """
        try:
            # validate showing and seats
            self._validate_showing_and_seats()
            
            # calculate base price
            self._calculate_base_price()
            
            # apply promotion (if provided)
            self._apply_promotion()
            
            # simulate payment
            payment_result = self._simulate_payment()
            
            # create booking and tickets
            self._create_booking_and_tickets()
            
            # return complete booking result
            return self._format_result(payment_result)
        
        except Exception as e:
            # log the error for debugging
            logger = logging.getLogger(__name__)
            logger.error(f"Booking failed: {str(e)}")
            raise

    def _validate_showing_and_seats(self):
        """
        Validate showing exists, is in future, and seats are available.
        """
        # validate showing exists
        try:
            self.showing = Showing.objects.get(showing_id=self.showing_id)
        except Showing.DoesNotExist:
            raise serializers.ValidationError(f"Showing with ID {self.showing_id} does not exist")
        
        # validate showing is in the future
        if self.showing.start_time < timezone.now():
            raise serializers.ValidationError("Cannot book tickets for past showings")
        
        # get all seat IDs
        seat_ids = [s['seat_id'] for s in self.seats_data]

        # check for duplicate seat selections
        if len(seat_ids) != len(set(seat_ids)):
            raise serializers.ValidationError("Cannot select the same seat multiple times")
        
        # validate each seat
        for seat_data in self.seats_data:
            try:
                seat = Seat.objects.get(seat_id=seat_data['seat_id'])
            except Seat.DoesNotExist:
                raise serializers.ValidationError(f"Seat with ID {seat_data['seat_id']} does not exist")
            
            # check seat belongs to correct showroom (compare objects)
            if seat.showroom_id != self.showing.showroom:
                raise serializers.ValidationError(
                    f"Seat {seat.row_label}{seat.seat_number} is not in {self.showing.showroom.showroom_name}"
                )
            
            # check seat availability
            if Ticket.objects.filter(showing=self.showing, seat=seat).exists():
                raise serializers.ValidationError(
                    f"Seat {seat.row_label}{seat.seat_number} is already booked for this showing"
                )
            
            # validate age category
            valid_categories = ['Child', 'Adult', 'Senior']
            if seat_data['age_category'] not in valid_categories:
                raise serializers.ValidationError(
                    f"Age category must be one of: {', '.join(valid_categories)}"
                )
            
            self.seats.append({
                'seat': seat,
                'age_category': seat_data['age_category']
            })
    
    def _calculate_base_price(self):
        """
        Calculate base price based on ticket types
        
        Pricing:
        - Child: $8.00
        - Adult: $12.00
        - Senior: $10.00
        """
        pricing = {
            'Child': 8.00,
            'Adult': 12.00,
            'Senior': 10.00
        }
        
        self.base_price = sum(
            pricing.get(seat_info['age_category'], 12.00)
            for seat_info in self.seats
        )
        
        # start with base price (will be modified by promotion)
        self.final_price = self.base_price
    
    def _apply_promotion(self):
        """
        Apply promotion using Factory Method pattern.
        """
        # Use Factory Method to get the correct promotion handler
        self.promotion = PromotionFactory.get_promotion(self.promo_code)
        
        # apply promotion to calculate final price
        if self.promotion.is_valid():
            self.final_price = self.promotion.apply(self.base_price)

    def _simulate_payment(self):
        """
        Simulate payment processing
        
        Returns:
            dict: Payment result with card info
        """
        payment_card_id = self.payment_info.get('payment_card_id')
        
        if payment_card_id:
            # use saved card
            try:
                card = PaymentCard.objects.get(pk=payment_card_id, user=self.user)
                
                # check if card is expired
                if card.is_expired():
                    raise serializers.ValidationError("Selected card is expired")
                
                return {
                    'payment_method': 'saved_card',
                    'last4': card.get_masked_card_number()[-4:],
                    'brand': card.brand,
                    'card_id': card.id
                }
            except PaymentCard.DoesNotExist:
                raise serializers.ValidationError("Selected payment card does not exist or does not belong to you")
        
        else:
            # process new card
            card_number = self.payment_info.get('card_number')
            expiration = self.payment_info.get('expiration')
            brand = self.payment_info.get('brand')
            
            if not all([card_number, expiration, brand]):
                raise serializers.ValidationError("Complete payment card information is required")
            
            # validate card number format
            card_digits = ''.join(filter(str.isdigit, card_number))
            if len(card_digits) < 13 or len(card_digits) > 19:
                raise serializers.ValidationError("Invalid card number format")
            
            # validate expiration date
            try:
                month, year = expiration.split('/')
                month = int(month)
                year = int(year)
                
                if month < 1 or month > 12:
                    raise serializers.ValidationError("Invalid expiration month")
                
                from datetime import datetime
                current_year = datetime.now().year
                current_month = datetime.now().month
                
                if year < current_year or (year == current_year and month < current_month):
                    raise serializers.ValidationError("Card is expired")
            except (ValueError, AttributeError):
                raise serializers.ValidationError("Expiration must be in MM/YYYY format")
            
            # simulate successful payment
            return {
                'payment_method': 'new_card',
                'last4': card_digits[-4:],
                'brand': brand,
                'card_number': card_digits  # Would be encrypted in production
            }

    def _create_booking_and_tickets(self):
        """
        Create booking and ticket records in the database
        """
        # Create the booking
        self.booking = Booking.objects.create(
            user=self.user,
            total_price=self.final_price,
            promo_code=self.promo_code or ''
        )
        
        # create tickets for each seat
        for seat_info in self.seats:
            ticket = Ticket.objects.create(
                booking=self.booking,
                showing=self.showing,
                seat=seat_info['seat'],
                age_category=seat_info['age_category']
            )
            self.tickets.append(ticket)

    def _format_result(self, payment_result):
        """
        Format and return the complete booking result
        
        Returns:
            dict: Complete booking information for API response
        """
        return {
            'booking_id': self.booking.booking_id,
            'user_email': self.user.email,
            'movie_title': self.showing.movie.movie_title,
            'showroom_name': self.showing.showroom.showroom_name,
            'start_time': self.showing.start_time,
            'seats': [
                {
                    'seat_display': f"{ticket.seat.row_label}{ticket.seat.seat_number}",
                    'age_category': ticket.age_category
                }
                for ticket in self.tickets
            ],
            'base_price': f"${self.base_price:.2f}",
            'promotion_applied': self.promotion.promo_code if self.promotion.is_valid() else None,
            'discount_display': self.promotion.get_discount_display(self.base_price),
            'final_price': f"${self.final_price:.2f}",
            'payment': payment_result,
            'booking_time': self.booking.booking_time
        }