#takes an object from the database (eg Movie) and converts it to JSON for API responses
#or, takes info from frontend (password= serializers...), validates fields, then creates/updates database objects
from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db import models
from .models import Profile, Movie, Promotion, PaymentCard, Address, Genre, MovieGenre, Showing, Showroom

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
# Serializes promotions and their discount details

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'discount_percentage']
        read_only_fields = ['promo_id', 'created_at']

# --- User Registration Serializer ---
# Creates new users and associated profiles

class RegisterSerializer(serializers.ModelSerializer):
    #receives data from frontend for registration and validates it
    password = serializers.CharField(write_only=True)
    subscribed = serializers.BooleanField(write_only=True, required=False, default=False)
    phone_number = serializers.CharField(required=True)


    class Meta:
        model = User #creating user model
        fields = ["username", "email", "phone_number", "password", "subscribed"]

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use")
        return value
    
    def validate_phone_number(self, value):
        """Phone validation"""
        phone_digits = ''.join(filter(str.isdigit, value))
        if len(phone_digits) < 10:
            raise serializers.ValidationError("Phone number must have at least 10 digits")
        return value

# Creates user and inactive profile (activated later)
    def create(self, validated_data):
        subscribed = validated_data.pop("subscribed", False)
        phone_number = validated_data.pop("phone_number")
        #create user (in auth_user table)
        user = User.objects.create_user(**validated_data)
        #create associated profile (in cinema_profile table)
        Profile.objects.create(user=user, phone_number=phone_number, subscribed=subscribed, status="Inactive")
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
    phone_number = serializers.CharField(required=False, allow_blank=True)
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
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
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
    phone_number = serializers.CharField()
    subscribed = serializers.BooleanField()
    status = serializers.CharField(read_only=True)
    class Meta:
        model = Profile
        fields = ["username", "email", "first_name", "last_name", "phone_number", "subscribed", "status"]