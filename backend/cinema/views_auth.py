import os
import smtplib
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Profile
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer

# --- Registration ---
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    def perform_create(self, serializer):
        user = serializer.save()
        print(f"User {user.username} registered successfully.")
        #false until they log in
        user.is_active = False
        user.save()
        print("Saved user")
        #link to verification
        verification_link = f"http://localhost:5173/api/verify/"
        print(f"Verification link: {verification_link}")
        #creates a six digit int
        rand_int = "123456"
        try:
            #smtp session created
            s = smtplib.SMTP('smtp.gmail.com', 587)
            #start TLS for security
            s.starttls()
            #authentication
            print(os.getenv("GMAIL_PASS"))
            s.login("cullenowens2005@gmail.com", os.getenv("GMAIL_PASS"))
            #message
            message = (
                f"Subject: CES Account Verification\n\n"
                f"Hello {user.username},\n\n"
                f"Please verify your account by clicking the following link:\n"
                f"{verification_link}\n\n"
                f"Your verification code is: {rand_int}\n\n"
                f"Thank you,\nCES Team"
            )
            #sending the mail
            s.sendmail("cullenowens2005@gmail.com", user.email, message)
            s.quit()

        except Exception as e:
            print(f"Error sending email: {e}")

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