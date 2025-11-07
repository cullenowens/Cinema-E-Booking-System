#creates function for the route from urls.oy
#creates the logic responsible for processing a request, in this case,
#for admin tasks and responsibilities in the website
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import generics
from rest_framework import status
from .models import Movie, Promotion
from .serializers import MovieSerializer, PromotionSerializer

#Managing Promotions
class AdminPromotionView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PromotionSerializer

    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        queryset = Promotion.objects.all()
#Managing Movies
class AdminMovieView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()