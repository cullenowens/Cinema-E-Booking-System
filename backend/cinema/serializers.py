from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, PaymentCard, Address

# File acts as a translator between the frontend and backend
# File helps convert Python objects to JSON and vice versa

class RegisterSerializer(serializers.ModelSerializer):
    # This line makes sure password is write-only and not returned in responses
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

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'zip_code']

    def create(self, validated_data):
        # automatically assign current user to the address
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
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
        """Validate card number format"""
        # first remove spaces and dashes from input
        clean_number = ''.join(value.split()).replace('-', '')
        
        # checks the length and if all characters are digits
        if not clean_number.isdigit() or len(clean_number) < 13 or len(clean_number) > 19:
            raise serializers.ValidationError("Invalid card number format")
        
        return clean_number
    
    # method to validate expiration date format MM/YYYY and check if expired
    def validate_expiration(self, value):
        """Validate MM/YYYY format"""
        if '/' not in value or len(value) != 7:
            raise serializers.ValidationError("Expiration must be in MM/YYYY format")
        
        try:
            month, year = value.split('/')
            month, year = int(month), int(year)
            
            #check to see if month is valid
            if month < 1 or month > 12:
                raise serializers.ValidationError("Invalid month")
                
            from datetime import datetime
            # check if year is in the past to signify expiration
            if year < datetime.now().year:
                raise serializers.ValidationError("Card is expired")
                
        except ValueError:
            raise serializers.ValidationError("Invalid expiration format")
        
        return value
    
    # method to create PaymentCard instance with encrypted card number
    def create(self, validated_data):
        """Create payment card with encryption"""
        # gets the card number from validated data and "encrypts" it by only storing last 4 digits
        card_number = validated_data.pop('card_number')
        validated_data['card_number_enc'] = f"ENC_{card_number[-4:]}"  # store last 4 digits
        
        # goes to the current user from request context and assigns it to the card
        validated_data['user'] = self.context['request'].user
        
        # calls the parent create method to save the instance
        return super().create(validated_data)
    
    # method to update PaymentCard instance (no card number changes allowed for security)
    def update(self, instance, validated_data):
        """Update card info (no card number changes for security)"""
        # removes card_number if someone tries to update it
        validated_data.pop('card_number', None)
        # updates other fields using parent update method
        return super().update(instance, validated_data)