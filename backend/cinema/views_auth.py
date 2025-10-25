from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Profile, PaymentCard, Address
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, PaymentCardSerializer, AddressSerializer

# --- Registration ---
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_mail(
            "Confirm your CES account",
            "Thank you for registering! (In dev mode, email is printed to console)",
            "no-reply@ces.com",
            [user.email],
            fail_silently=True,
        )

# --- Login ---
class LoginView(APIView):
    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = authenticate(username=s.validated_data["username"], password=s.validated_data["password"])

        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        # Check if user is active
        profile = getattr(user, "profile", None)
        if profile and profile.status != "Active":
            return Response({"error": "Account not activated"}, status=403)

        tokens = RefreshToken.for_user(user)
        return Response({
            "access": str(tokens.access_token),
            "refresh": str(tokens),
            "user": {"username": user.username, "email": user.email},
        })

# --- Logout ---
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"message": "Logout successful"})

# --- Profile ---
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        return Response(ProfileSerializer(profile).data)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Security: Email notification after profile change
        send_mail(
            "Profile updated",
            "Your CES profile was updated.",
            "no-reply@ces.com",
            [request.user.email],
            fail_silently=True,
        )
        return Response(serializer.data)
    

# --- Address ---
class AddressView(APIView):
    """handle user address operations (GET, POST, PUT)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """get user's address"""
        try:
            # gets the address for the logged in user
            address = Address.objects.get(user=request.user)
            return Response(AddressSerializer(address).data)
        except Address.DoesNotExist:
            return Response({"error": "No address found"}, status=404)

    def post(self, request):
        """create user's address"""
        # check if user already has an address (one-to-one relationship)
        if Address.objects.filter(user=request.user).exists():
            return Response({"error": "Address already exists. Use PUT to update."}, status=400)
        
        # makes sure the address is linked to the current user and saves it
        serializer = AddressSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        return Response(AddressSerializer(address).data, status=201)

    def put(self, request):
        """update user's address"""
        try:
            # gets the address for the logged in user
            address = Address.objects.get(user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "No address found"}, status=404)
        
        # takes the existing address and updates it with new data
        serializer = AddressSerializer(address, data=request.data, partial=True, context={'request': request})
        # checks to see if the format of the new data is valid
        serializer.is_valid(raise_exception=True)
        # save the updated address
        address = serializer.save()
        # returns the updated address data to the frontend
        return Response(AddressSerializer(address).data)
    
# --- Payment Cards (creation view) ---
class PaymentCardView(APIView):
    """handle payment card list operations (GET all cards, POST new card)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """get all payment cards for current user"""
        # filter cards by current user and order by newest first
        cards = PaymentCard.objects.filter(user=request.user).order_by('-id')
        # use serializer to convert to JSON format, returns to frontend
        return Response(PaymentCardSerializer(cards, many=True).data)

    def post(self, request):
        """add new payment card for current user"""
        # limit number of cards per user (just for now)
        if PaymentCard.objects.filter(user=request.user).count() >= 4:
            return Response({
                "error": "Maximum of 4 payment cards allowed per user"
            }, status=400)

        # create serializer with request data and context
        serializer = PaymentCardSerializer(data=request.data, context={'request': request})
        # checks to see if the format of the new data is valid and raises error if not to frontend
        serializer.is_valid(raise_exception=True)
        # save the new card to the database
        card = serializer.save()
        
        # send email notification to user that a new card was added
        send_mail(
            "New Payment Card Added",
            f"A new {card.brand} card ending in {card.card_number_enc[-4:]} was added to your account.",
            "no-reply@ces.com",
            [request.user.email],
            fail_silently=True,
        )
        
        # return the created card data
        return Response(PaymentCardSerializer(card).data, status=201)
    
# --- Payment Card Detail (individual card view) ---
class PaymentCardDetailView(APIView):
    """handle individual payment card operations (GET one, PUT update, DELETE)"""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        """get payment card by ID for current user only (security)"""
        try:
            # only return card if it belongs to current user
            return PaymentCard.objects.get(pk=pk, user=self.request.user)
        except PaymentCard.DoesNotExist:
            return None

    def get(self, request, pk):
        """get specific payment card by ID"""
        card = self.get_object(pk)
        if not card:
            return Response({"error": "Payment card not found"}, status=404)
        
        return Response(PaymentCardSerializer(card).data)

    def put(self, request, pk):
        """update payment card (brand, expiration only, no card number changes)"""
        card = self.get_object(pk)
        if not card:
            return Response({"error": "Payment card not found"}, status=404)

        # update card with new data (partial=True allows updating only some fields)
        serializer = PaymentCardSerializer(card, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_card = serializer.save()
        
        # send email notification about update
        send_mail(
            "Payment Card Updated",
            f"Your {updated_card.brand} card was updated.",
            "no-reply@ces.com",
            [request.user.email],
            fail_silently=True,
        )
        
        return Response(PaymentCardSerializer(updated_card).data)
    
    def delete(self, request, pk):
        """delete payment card permanently"""
        card = self.get_object(pk)
        if not card:
            return Response({"error": "Payment card not found"}, status=404)

        # store card info for email notification before deletion
        card_info = f"{card.brand} ending in {card.card_number_enc[-4:]}"
        
        # actually delete the card from database (permanent removal)
        card.delete()
        
        # send email notification about deletion
        send_mail(
            "Payment Card Removed",
            f"Your {card_info} was removed from your account.",
            "no-reply@ces.com",
            [request.user.email],
            fail_silently=True,
        )
        
        # return success message (status 204 = No Content)
        return Response({"message": "Payment card deleted successfully"}, status=204)