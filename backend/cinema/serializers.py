from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Movie, Promotion

class MovieSerializer(serializers.ModelSerializer):
    #genres = GenreSerializer(many=True, source='moviegenre_set', read_only=True)
    #showtimes = MovieShowtimeSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['movie_id', 'movie_title', 'movie_description', 'age_rating', 'poster_url', 'trailer_url', 'movie_status', 'genres', 'showtimes']

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'discount_percentage']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    subscribed = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "subscribed"]

    def perform_create(self, validated_data):
        subscribed = validated_data.pop("subscribed", False)
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, subscribed=subscribed, status="Inactive")
        return user
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # <-- this will tell you exactly what’s wrong
        serializer.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)
    
class AdminRegisterSerializer(serializers.ModelSerializer):
    #for crearting admin users
    #could look into hardcoding admin users
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_staff = True
        user.save()
        Profile.objects.create(user=user, status="Active", subscribed=True)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["phone", "subscribed", "status"]