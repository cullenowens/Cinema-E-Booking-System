from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    subscribed = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "subscribed"]

    def create(self, validated_data):
        subscribed = validated_data.pop("subscribed", False)
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, subscribed=subscribed, status="Inactive")
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["phone", "subscribed", "status"]