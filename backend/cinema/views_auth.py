#creates function for the route from urls.oy
#creates the logic responsible for processing a request, in this case,
#user registration, login, logout, profile management, payment cards, address management
'''
The purpose of this file is to handle all user authentication and profile management functionality.

Includes:
- User registration with email verification
- Login/logout with JWT tokens
- Password reset (forgot password)
- User profile management (view/edit)
- Billing address management
- Payment card management (encrypted storage)
'''
import os
import smtplib
import random
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from .models import Profile, PaymentCard, Address
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, PaymentCardSerializer, AddressSerializer

# --- Registration ---
class RegisterView(generics.CreateAPIView):
   
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # prints for debugging
        print("User registered successfully!:", user.username)
        
        # will be inactive until email verified
        user.is_active = False
        user.save()
        print("User is inactive until email is verified.")

        # generate random 6-digit verification code
        verification_code = str(random.randint(100000, 999999))
        print(f"Generated verification code: {verification_code}")

        # create/get profile and save verification code
        try:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.verification_code = verification_code
            profile.verification_code_created_at = timezone.now()
            profile.status = "Inactive"  # status set to Inactive
            profile.save()
            print(f"Verification code saved to database: {verification_code}")
        except Exception as e:
            print(f"Error saving verification code: {e}")
            return
        
        #link to verification
        verification_link = f"http://localhost:5173/verify?email={user.email}"
        print(f"Verification link: {verification_link}")
        
        try:
            #smtp session created
            s = smtplib.SMTP('smtp.gmail.com', 587)
            #start TLS for security
            s.starttls()

            # Get Gmail credentials from environment variables
            gmail_email = os.getenv("GMAIL_EMAIL")
            gmail_password = os.getenv("GMAIL_PASS")

            #authentication
            print(f"Gmail email: {gmail_email}")
            print(f"Gmail password loaded: {'Yes' if gmail_password else 'No'}")

            # login to gmail
            s.login(gmail_email, gmail_password)

            #message
            message = (
                f"Subject: CES Account Verification\n\n"
                f"Hello {user.username},\n\n"
                f"Thank you for registering with Cinema E-Booking System!\n\n"
                f"Please verify your account by entering the following code:\n"
                f"{verification_code}\n\n"
                f"Go to: {verification_link}\n\n"
                f"This code will expire in 15 minutes.\n\n"
                f"Thank you,\nCES Team"
            )

            #sending the mail
            s.sendmail(gmail_email, user.email, message)
            s.quit()
            print(f"Verification email sent to {user.email}")

        except Exception as e:
            print(f"Error sending email: {e}")
            pass

# --- Login ---
class LoginView(APIView):
    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = authenticate(username=s.validated_data["username"], password=s.validated_data["password"])

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if user is active (email verified)
        if not user.is_active:
            return Response({
                "error": "Please verify your email before logging in",
                "code": "EMAIL_NOT_VERIFIED"
            }, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        #getting remember_me from data
        remember_me = s.validated_data.get("remember_me", False)

        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=7))
        #otherwise default settings
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        })

# --- Logout ---
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

# --- Profile ---
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            #profile = Profile.objects.get(user=request.user)
            #serializer = ProfileSerializer(profile)
            user = request.user
            return Response({
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.profile.phone,
                "subscribed": user.profile.subscribed,
                "status": user.profile.status
            })
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:

            user = request.user
            profile = user.profile
            
            # Update User fields
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            user.email = request.data.get('email', user.email)
            user.save()
            
            # Update Profile fields
            profile.phone = request.data.get('phone', profile.phone)
            profile.subscribed = request.data.get('subscribed', profile.subscribed)
            profile.save()
            
            return Response({'message': 'Profile updated successfully'})
    
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        

@api_view(['POST'])
def verify_email(request):
    """
    Verify user email address using a 6-digit code sent via email during registration.

    **Endpoint:** POST /api/auth/verify/
    
    **Authentication:** Not required
    
    **Input (JSON):**
        {
            "email": "john@example.com",      // Required, registered email
            "verification_code": "123456"     // Required, 6-digit code from email
        }

    **Output (Success - 200 OK):**
        {
            "message": "Email verified successfully! You can now login.",
            "success": true
        }

    **Output (Error - 400 Bad Request):**
        {
            "error": "Email and verification code are required"
        }
        // OR
        {
            "error": "Invalid or expired verification code"
        }
        // OR
        {
            "error": "User not found"
        }
    
    **Behavior:**
        1. Looks up user by email
        2. Validates verification code
        3. Checks if code expired (5-minute expiration)
        4. Activates user account (sets is_active=True)
        5. Deletes verification token
    
    **Code Expiration:**
        - Codes expire 5 minutes after creation
        - Expired codes return error
        - User must request new code via registration or forgot password
    
    **After Verification:**
        - User account becomes active
        - User can now login with POST /api/auth/login/
    """
    try:
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        
        if not email or not verification_code:
            return Response({
                'error': 'Email and verification code are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # find the most recent INACTIVE user with this email
        user = User.objects.filter(
            email=email, 
            is_active=False
        ).order_by('-date_joined').first()
        
        if not user:
            # check if user already verified
            active_user = User.objects.filter(email=email, is_active=True).first()
            if active_user:
                return Response({
                    'message': 'Account already verified'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'No pending verification found for this email'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Get user profile and check code
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        #Check if code expired (5 minutes)
        if profile.verification_code_created_at:
            expiration_time = profile.verification_code_created_at + timedelta(minutes=5)
            if timezone.now() > expiration_time:
                return Response({
                    'error': 'Verification code has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify code matches
        if profile.verification_code == verification_code:
            # SUCCESS: Activate the user
            user.is_active = True
            user.save()
            
            # Update profile status and clear verification code
            profile.status = "Active"
            profile.verification_code = None
            profile.verification_code_created_at = None
            profile.save()
            
            print(f"User {user.username} verified successfully!")
            
            return Response({
                'message': 'Email verified successfully! You can now login.',
                'success': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid verification code'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Verification failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ForgotPasswordView(APIView):
    #when password reset is requested, send code to email
    def post(self, request):
        try:
            email = request.data.get('email')
            
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            #finding user (has to be active)
            user = User.objects.filter(email=email, is_active=True).first()
            #case if user doesnt exist, won't show the email exists
            if not user:
                return Response({
                    'message': 'If an account with that email exists, a reset code has been sent.'
                }, status=status.HTTP_200_OK)
            
            reset_code = str(random.randint(100000, 999999))

            try:
                profile = Profile.objects.get(user=user)
                #just reuses verification code field
                profile.verification_code = reset_code
                profile.verification_code_created_at = timezone.now()
                profile.save()
                print(f"Password reset code saved to database: {reset_code}")
            except Profile.DoesNotExist:
                return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                
                gmail_email = os.getenv("GMAIL_EMAIL")
                gmail_password = os.getenv("GMAIL_PASS")
                
                s.login(gmail_email, gmail_password)
                
                message = (
                    f"Subject: CES Password Reset\n\n"
                    f"Hello {user.username},\n\n"
                    f"You requested to reset your password.\n\n"
                    f"Your password reset code is:\n"
                    f"{reset_code}\n\n"
                    f"This code will expire in 15 minutes.\n\n"
                    f"If you didn't request this, please ignore this email.\n\n"
                    f"Thank you,\nCES Team"
                )
                
                s.sendmail(gmail_email, user.email, message)
                s.quit()
                print(f"Reset email sent to {user.email}")
                
            except Exception as e:
                print(f"Error sending reset email: {e}")
            
            return Response({
                'message': 'If an account exists with this email, a reset code has been sent'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Reset request failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ResetPasswordView(APIView):
    #called when user is already logged in
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({'error': 'Current and new passwords are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        if current_password == new_password:
            return Response({'error': 'New password must be different from current password'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({'error': 'New password must be at least 8 characters long'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()

        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


# --- Address ---
class AddressView(APIView):
    """
    Manage user's billing address (one address per user).
    
    **Endpoint:** GET/POST/PUT /api/auth/address/
    
    **Authentication:** Required (IsAuthenticated)
    
    **Headers:**
        Authorization: Bearer <access_token>

        
    **GET REQUEST**
    -----------
    Retrieve user's billing address.
    
    **Input:** None (user from JWT token)
    
    **Output (Success - 200 OK):**
        {
            "id": 1,
            "street": "123 Main St",
            "city": "Atlanta",
            "state": "GA",
            "zip_code": "30309"
        }
    
    **Output (No Address - 404 Not Found):**
        {
            "error": "Address not found"
        }

        
    **POST REQUEST**
    -----------
    Create new billing address (only if user has none).
    
    **Input (JSON):**
        {
            "street": "123 Main St",          // Required, max 255 chars
            "city": "Atlanta",                // Required, max 100 chars
            "state": "GA",                    // Required, 2-char state code
            "zip_code": "30309"               // Required, 5 or 9 digits
        }
    
    **Output (Success - 201 Created):**
        {
            "id": 1,
            "street": "123 Main St",
            "city": "Atlanta",
            "state": "GA",
            "zip_code": "30309"
        }

    **Output (Error - 400 Bad Request):**
        {
            "error": "User already has an address. Use PUT to update."
        }
        // OR
        {
            "street": ["This field is required"],
            "zip_code": ["Enter a valid zip code"]
        } 

        
     **PUT REQUEST**
    -----------
    Update existing billing address.
    
    **Input (JSON):**
        {
            "street": "456 New St",           // Optional
            "city": "Atlanta",                // Optional
            "state": "GA",                    // Optional
            "zip_code": "30310"               // Optional
        }
        // Send only fields to update
    
    **Output (Success - 200 OK):**
        {
            "id": 1,
            "street": "456 New St",
            "city": "Atlanta",
            "state": "GA",
            "zip_code": "30310"
        } 

    **Output (Error - 404 Not Found):**
        {
            "error": "Address not found. Use POST to create."
        }
    
    **Validation:**
        - Street: Required, max 255 characters
        - City: Required, max 100 characters
        - State: Required, 2 uppercase letters (e.g., GA, CA, NY)
        - Zip Code: Required, format: 12345 or 12345-6789
    
    **Limitations:**
        - One address per user (for billing)
        - Cannot delete address (use PUT to update)
        - Address is used for payment processing

    """
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
    """
    Manage user's payment cards (max 4 cards per user, encrypted storage).

    **Endpoint:** GET/POST /api/auth/payment-cards/
    
    **Authentication:** Required (IsAuthenticated)
    
    **Headers:**
        Authorization: Bearer <access_token>

        
    **GET REQUEST**
    -----------
    List all saved payment cards for user.
    
    **Input:** None (user from JWT token)
    
    **Output (Success - 200 OK):**
        [
            {
                "id": 1,
                "brand": "Visa",
                "card_number_enc": "****1234",    // Last 4 digits only
                "expiration": "12/2025"
            },
            {
                "id": 2,
                "brand": "Mastercard",
                "card_number_enc": "****5678",
                "expiration": "06/2026"
            }
        ]

    **Output (No Cards - 200 OK):**
        []

    
     **POST REQUEST**
    -----------
    Add new payment card (encrypted, sends email notification).
    
    **Input (JSON):**
        {
            "card_number": "4111111111111111", // Required, 13-19 digits
            "brand": "Visa",                   // Required (Visa, Mastercard, Amex, Discover)
            "expiration": "12/2025"            // Required, format: MM/YYYY
        }
    
    **Output (Success - 201 Created):**
        {
            "id": 3,
            "brand": "Visa",
            "card_number_enc": "****1111",
            "expiration": "12/2025"
        }

    **Output (Error - 400 Bad Request):**
        {
            "error": "You can only store up to 4 payment cards"
        }
        // OR
        {
            "card_number": ["Enter a valid card number"],
            "expiration": ["Invalid expiration date"]
        }

    **Card Number Encryption:**
        - Full card number encrypted with Fernet symmetric encryption
        - Only last 4 digits stored in plaintext for display
        - Encryption key stored in environment variable
        - Card numbers never returned in API responses (security)
    
    **Email Notification:**
        When card is added, user receives email:
        Subject: "New Payment Card Added"
        Body: "A new Visa ending in 1234 was added to your account."
    
    **Validation:**
        - Card Number: Must be valid format (Luhn algorithm)
        - Brand: Must be Visa, Mastercard, American Express, or Discover
        - Expiration: Format MM/YYYY, must be future date
        - Max Cards: 4 cards per user
    
    **Security:**
        - Card numbers encrypted at rest
        - SSL/TLS encryption in transit
        - PCI compliance considerations
        - User notification on card changes

    """
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
    """
    Handles individual payment card operations by ID for the authenticated user.

    **Endpoint:** GET/PUT/DELETE /api/auth/payment-cards/<id>/
    
    **Authentication:** Required (IsAuthenticated)
    
    **Headers:**
        Authorization: Bearer <access_token>

    **GET REQUEST**
    -----------
    Retrieve specific payment card details.
    
    **URL:** GET /api/auth/payment-cards/3/
    
    **Input:** Card ID in URL
    
    **Output (Success - 200 OK):**
        {
            "id": 3,
            "brand": "Visa",
            "card_number_enc": "****1234",
            "expiration": "12/2025"
        }
    
    **Output (Error - 404 Not Found):**
        {
            "error": "Payment card not found"
        }

    
    **PUT REQUEST**
    ---
    Update payment card (brand and expiration only, NOT card number).
    
    **URL:** PUT /api/auth/payment-cards/3/
    
    **Input (JSON):**
        {
            "brand": "Mastercard",            // Optional
            "expiration": "06/2026"           // Optional
        }
        // Note: Cannot update card_number for security
    
    **Output (Success - 200 OK):**
        {
            "id": 3,
            "brand": "Mastercard",
            "card_number_enc": "****1234",
            "expiration": "06/2026"
        }
    
    **Output (Error - 400 Bad Request):**
        {
            "expiration": ["Invalid expiration date"]
        }

    
    **DELETE REQUEST**
    ---
    Permanently delete payment card (sends email notification).
    
    **URL:** DELETE /api/auth/payment-cards/3/
    
    **Input:** Card ID in URL
    
    **Output (Success - 200 OK):**
        {
            "message": "Payment card deleted successfully"
        }
    
    **Output (Error - 404 Not Found):**
        {
            "error": "Payment card not found"
        }


    **Email Notification (on delete):**
        Subject: "Payment Card Removed"
        Body: "Your Visa card ending in 1234 was removed from your account."
    
    **Security:**
        - Users can only access their own cards
        - Card number cannot be updated (must delete and re-add)
        - Email notifications for all card changes
        - Deletion is permanent (cannot be undone)
    
    **Why Card Number Cannot Be Updated:**
        - Security best practice
        - Prevents card number changes without full validation
        - Forces user to re-enter full card number
        - Maintains audit trail 
    """
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
