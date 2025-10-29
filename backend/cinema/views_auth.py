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
from .models import Profile
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer

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
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        

@api_view(['POST'])
def verify_email(request):
    """Verify user email with verification code"""
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
    #using verif code, reset password
    def post(self, request):
        try:
            email = request.data.get('email')
            reset_code = request.data.get('reset_code')
            new_password = request.data.get('new_password')

            if not email or not reset_code or not new_password:
                return Response({'error': 'Email, reset code, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            #find user (has to be active)
            user = User.objects.filter(email=email, is_active=True).first()

            if not user:
                return Response({'error': 'Invalid email or reset code'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if profile.verification_code_created_at:
                expiration_time = profile.verification_code_created_at + timedelta(minutes=5)
                if timezone.now() > expiration_time:
                    return Response({
                        'error': 'Verification code has expired'
                    }, status=status.HTTP_400_BAD_REQUEST)

            if profile.verification_code != reset_code:
                return Response({'error': 'Invalid reset code'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()

            #clear reset code
            profile.verification_code = None
            profile.save()

            print(f"User {user.username} password reset successfully")
            return Response({'message': 'Password reset successful', 'success': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Password reset failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
