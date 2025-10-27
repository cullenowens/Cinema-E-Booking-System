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