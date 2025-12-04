'''
User Portal Views
takes care of the seat selection, booking creation, and booking history retrieval for users.
'''

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from collections import defaultdict
import logging
import smtplib
import os
from dotenv import load_dotenv
from datetime import datetime

from .models import Showing, Showroom, Seat, Booking, Ticket, Movie
from .serializers import (
    ShowingDetailSerializer,
    SeatMapSerializer,
    SeatAvailabilitySerializer,
    BookingCreateSerializer,
    BookingDetailSerializer,
    TicketSerializer
)
load_dotenv()
logger = logging.getLogger(__name__)

# Browse available showings 

class ShowingListView(APIView):
    '''
    List all future showings with availability information.

    purpose is user browse all available showtimes.

    GET /api/user/showings/
    
    Query parameters:
    - movie_id: Filter by specific movie (optional)
    - date: Filter by date YYYY-MM-DD (optional)
    - showroom_id: Filter by showroom (optional)
    
    Example response:
    {
        "count": 5,
        "showings": [
            {
                "showing_id": 42,
                "movie_title": "Inception",
                "movie_poster": "https://...",
                "showroom_name": "Theater 1",
                "start_time": "2025-11-15T19:30:00Z",
                "available_seats": 95,
                "total_seats": 100
            },
            ...
        ]
    }
    '''
    permission_classes = []

    def get(self, request):
        '''
        List showings with optional filtering.
        '''
        try:
            # start with future showings only
            showings = Showing.objects.filter(
                start_time__gte=timezone.now()
            ).select_related('movie', 'showroom').order_by('start_time')

            # optional filters
            movie_id = request.query_params.get('movie_id')
            date = request.query_params.get('date')
            showroom_id = request.query_params.get('showroom_id')

            if movie_id:
                showings = showings.filter(movie_id=movie_id)
            
            if date:
                # Filter by date (ignoring time)
                try:
                    filter_date = datetime.strptime(date, '%Y-%m-%d').date()
                    showings = showings.filter(start_time__date=filter_date)
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if showroom_id:
                showings = showings.filter(showroom_id=showroom_id)

            # Serialize showings with availability
            serializer = ShowingDetailSerializer(showings, many=True)
            
            logger.info(f"Listed {showings.count()} showings")
            
            return Response({
                'count': showings.count(),
                'showings': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing showings: {e}")
            return Response(
                {"error": "Failed to retrieve showings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ShowingDetailView(APIView):
    """
    Get detailed information about a specific showing.
    
    Purpose: User selects a showing to view details before booking.
    
    GET /api/user/showings/<showing_id>/
    
    Example response:
    {
        "showing_id": 42,
        "movie_id": 5,
        "movie_title": "Inception",
        "movie_poster": "https://...",
        "showroom_id": 1,
        "showroom_name": "Theater 1",
        "start_time": "2025-11-15T19:30:00Z",
        "end_time": "2025-11-15T22:00:00Z",
        "available_seats": 95,
        "total_seats": 100
    }
    """
    permission_classes = []

    def get(self, request, pk):
        """Get showing details"""
        try:
            showing = Showing.objects.select_related('movie', 'showroom').get(
                showing_id=pk,
                start_time__gte=timezone.now()  # Only future showings
            )
            
            serializer = ShowingDetailSerializer(showing)
            
            logger.info(f"Retrieved showing details: {showing}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Showing.DoesNotExist:
            return Response(
                {"error": "Showing not found or already started"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving showing: {e}")
            return Response(
                {"error": "Failed to retrieve showing details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Seat map views: view and select seats

class SeatMapView(APIView):
    '''
    Get complete seat map for a showing with availability.
    
    Purpose: Display interactive seat selection page.
    
    GET /api/user/showings/<showing_id>/seats/
    
    Example response:
    {
        "showing": {
            "showing_id": 42,
            "movie_title": "Inception",
            "start_time": "2025-11-15T19:30:00Z",
            "showroom_name": "Theater 1"
        },
        "seats_by_row": {
            "A": [
                {"seat_id": 1, "seat_number": 1, "is_available": true},
                {"seat_id": 2, "seat_number": 2, "is_available": false},
                ...
            ],
            "B": [...],
            ...
        },
        "total_seats": 100,
        "available_seats": 95
    }
    '''
    permission_classes = []  # Public - anyone can view seat map

    def get(self, request, pk):
        """Get seat map for showing"""
        try:
            # Get showing
            showing = Showing.objects.select_related('movie', 'showroom').get(
                showing_id=pk,
                start_time__gte=timezone.now()
            )
            
            # Get all seats for this showroom, ordered by row and number
            seats = Seat.objects.filter(
                showroom_id=showing.showroom
            ).order_by('row_label', 'seat_number')
            
            # Calculate totals
            total_seats = seats.count()
            booked_seats = Ticket.objects.filter(showing=showing).count()
            available_seats = total_seats - booked_seats
            
            # Prepare data for serializer
            seat_map_data = {
                'showing': showing,
                'seats': seats,
                'total_seats': total_seats,
                'available_seats': available_seats
            }

            # Serialize with showing_id in context for availability checks
            serializer = SeatMapSerializer(seat_map_data)
            
            logger.info(f"Generated seat map for showing {pk}: {available_seats}/{total_seats} available")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Showing.DoesNotExist:
            return Response(
                {"error": "Showing not found or already started"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error generating seat map: {e}")
            return Response(
                {"error": "Failed to generate seat map"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class SeatAvailabilityView(APIView):
    """
    Check availability of specific seats for a showing.
    
    Purpose: Real-time availability check before booking.
    
    POST /api/user/showings/<showing_id>/check-seats/
    
    Request body:
    {
        "seat_ids": [5, 6, 7]
    }
    
    Response:
    {
        "showing_id": 42,
        "seats": [
            {"seat_id": 5, "seat_display": "A5", "is_available": true},
            {"seat_id": 6, "seat_display": "A6", "is_available": true},
            {"seat_id": 7, "seat_display": "A7", "is_available": false}
        ],
        "all_available": false
    }
    """
    permission_classes = []

    def post(self, request, pk):
        """Check seat availability"""
        try:
            # Validate showing exists and is future
            showing = Showing.objects.get(
                showing_id=pk,
                start_time__gte=timezone.now()
            )
            
            # Get seat IDs from request
            seat_ids = request.data.get('seat_ids', [])
            
            if not seat_ids:
                return Response(
                    {"error": "seat_ids is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get seats
            seats = Seat.objects.filter(
                seat_id__in=seat_ids,
                showroom_id=showing.showroom
            )
        
            if seats.count() != len(seat_ids):
                return Response(
                    {"error": "Some seats not found or not in correct showroom"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serialize with availability info
            serializer = SeatAvailabilitySerializer(
                seats,
                many=True,
                context={'showing_id': pk}
            )
            
            # Check if all seats are available
            all_available = all(seat['is_available'] for seat in serializer.data)
            
            return Response({
                'showing_id': pk,
                'seats': serializer.data,
                'all_available': all_available
            }, status=status.HTTP_200_OK)
        
        except Showing.DoesNotExist:
            return Response(
                {"error": "Showing not found or already started"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error checking seat availability: {e}")
            return Response(
                {"error": "Failed to check seat availability"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
# Booking views: create and manage bookings

class BookingCreateView(APIView):
    '''
    creates a new booking with tickets.

    purpose is to do checkout process where user confirms seat selection.

    uses Facade Pattern to coordinate the entire booking process
    uses Factory Method Pattern to apply promotions

    Request body:
    {
        "showing_id": 42,
        "seats": [
            {"seat_id": 5, "age_category": "Adult"},
            {"seat_id": 6, "age_category": "Child"},
            {"seat_id": 7, "age_category": "Senior"}
        ],
        "promo_code": "SUMMER20",  # Optional
        "payment_card_id": 3,  # Use saved card OR provide new card:
        "card_number": "4532123456789012",
        "expiration": "12/2026",
        "brand": "Visa"
    }
    
    Response:
    {
        "booking_id": 123,
        "user_email": "john@email.com",
        "movie_title": "Inception",
        "showroom_name": "Theater 1",
        "start_time": "2025-11-15T19:30:00Z",
        "seats": [
            {"seat_display": "A5", "age_category": "Adult"},
            {"seat_display": "A6", "age_category": "Child"}
        ],
        "base_price": "$20.00",
        "promotion_applied": "SUMMER20",
        "discount_display": "20% off (-$4.00)",
        "final_price": "$16.00",
        "payment": {
            "payment_method": "saved_card",
            "last4": "9012",
            "brand": "Visa"
        },
        "booking_time": "2025-12-03T10:30:00Z"
    }
    '''
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        creates a booking using BookingFacade
        
        the facade coordinates:
        seat validation
        price calculation
        promotion application (Factory Method)
        payment simulation
        booking and ticket creation
        """
        try:
            # validate and create booking using BookingCreateSerializer
            # this serializer uses the BookingFacade internally
            serializer = BookingCreateSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                logger.warning(f"Booking validation failed: {serializer.errors}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # serializer.save() calls BookingFacade.process_booking()
            # which returns the complete formatted result
            result = serializer.save()
            #creates booking and tickets
            booking = result['booking']
            tickets = result['tickets']
            
            logger.info(
                f"Booking created: #{result['booking_id']} "
                f"by {request.user.username} "
                f"for {result['final_price']}"
            )
            #booking confirmation email logic
            try:
                user = request.user
                #get booking details
                movie_title = tickets[0].showing.movie.movie_title
                showroom_name = tickets[0].showing.showroom.showroom_name
                start_time = tickets[0].showing.start_time.strftime("%Y-%m-%d %H:%M")
                #build ticket list
                ticket_details = []
                total_price = 0
                for ticket in tickets:
                    ticket_details.append(
                        f"Seat: {ticket.seat.__str__()}, Category: {ticket.age_category}, Price: ${ticket.price:.2f}"
                    )
                    total_price += ticket.price
                ticket_list = "\n".join(ticket_details)
                #email sending
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
                #email message
                message = (
                    f"Subject: Booking Confirmation - {movie_title}\n\n"
                    f"Hello {user.username},\n\n"
                    f"Thank you for your booking with Cinema E-Booking System!\n\n"
                    f"Your booking has been confirmed. Here are your details:\n\n"
                    f"BOOKING CONFIRMATION\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Booking ID: #{booking.booking_id}\n"
                    f"Movie: {movie_title}\n"
                    f"Theater: {showroom_name}\n"
                    f"Showtime: {start_time}\n\n"
                    f"YOUR TICKETS:\n"
                    f"{ticket_list}\n\n"
                    f"TOTAL PRICE: ${total_price:.2f}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Please arrive 15 minutes before showtime.\n"
                    f"Present this confirmation email or your Booking ID at the theater.\n\n"
                    f"Need to make changes? Log in to your account to view or cancel your booking.\n\n"
                    f"Enjoy the show!\n\n"
                    f"Cinema E-Booking System Team"
                )
                #sends the mail
                s.sendmail(gmail_email, user.email, message)
                s.quit()
                print(f"Booking email sent to {user.email}")
            except Exception as e:
                print(f"Failed to send booking confirmation email: {e}")
                logger.error(f"Failed to send booking confirmation email: {e}")
                pass  # continue even if email fails
            
            # return the formatted result from Facade (not BookingDetailSerializer!)
            return Response(
                result,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return Response(
                {"error": "Failed to create booking. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookingListView(APIView):
    '''
    List user's past and upcoming bookings.

    purpose is user view their booking history and details.

    GET /api/user/bookings/
    
    Example response:
    {
        "count": 3,
        "bookings": [
            {
                "booking_id": 123,
                "movie_title": "Inception",
                "showroom_name": "Theater 1",
                "start_time": "2025-11-15T19:30:00Z",
                "tickets": [
                    {"seat_display": "A5", "age_category": "Adult", "price": 12.00},
                    {"seat_display": "A6", "age_category": "Child", "price": 8.00}
                ],
                "total_price": 20.00
            },
            ...
        ]
    }
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List user's bookings"""
        try:
            # gets all the bookings for the logged-in user
            bookings = Booking.objects.filter(
                user=request.user
            ).prefetch_related(
                'tickets',
                'tickets__showing',
                'tickets__showing__movie',
                'tickets__showing__showroom',
                'tickets__seat'
            ).order_by('-booking_id')  # orders it by most recent first
            
            serializer = BookingDetailSerializer(bookings, many=True)
            
            logger.info(f"Retrieved {bookings.count()} bookings for {request.user.username}")

            return Response({
                'count': bookings.count(),
                'bookings': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing bookings: {e}")
            return Response(
                {"error": "Failed to retrieve bookings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class BookingDetailView(APIView):
    '''
    Get detailed information about a specific booking.

    purpose is user view specific booking details for confirmation or receipt.

    GET /api/user/bookings/<booking_id>/

    Response:
    {
        "booking_id": 123,
        "user_email": "john@email.com",
        "movie_title": "Inception",
        "showroom_name": "Theater 1",
        "start_time": "2025-11-15T19:30:00Z",
        "tickets": [
            {"seat_display": "A5", "age_category": "Adult", "price": 12.00},
            ...
        ],
        "total_price": 30.00
    }
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Get booking details"""
        try:
            booking = Booking.objects.prefetch_related(
                'tickets',
                'tickets__showing',
                'tickets__showing__movie',
                'tickets__showing__showroom',
                'tickets__seat'
            ).get(
                booking_id=pk,
                user=request.user  # Security: only owner can view
            )
            
            serializer = BookingDetailSerializer(booking)
            
            logger.info(f"Retrieved booking details: #{pk} for {request.user.username}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found or you don't have permission to view it"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving booking: {e}")
            return Response(
                {"error": "Failed to retrieve booking details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """
        Cancels the booking (delete booking and tickets).
        
        purpose is user cancel their booking and get a refund.
        
        DELETE /api/user/bookings/<booking_id>/
        
        Response:
        {
            "message": "Booking cancelled successfully",
            "refunded_seats": ["A5", "A6", "A7"]
        }
        """
        try:
            # gets bookings for authenticated users only
            booking = Booking.objects.prefetch_related('tickets').get(
                booking_id=pk,
                user=request.user
            )
            
            # Check if showing hasn't started yet
            first_ticket = booking.tickets.first()
            if first_ticket and first_ticket.showing.start_time < timezone.now():
                return Response(
                    {"error": "Cannot cancel booking for past showings"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get seat info before deletion (for response)
            seat_info = [
                ticket.seat.__str__() for ticket in booking.tickets.all()
            ]
            
            # delete the booking and the tickets will be cascade deleted automatically
            booking.delete()
            
            logger.info(
                f"Booking cancelled: #{pk} by {request.user.username} "
                f"({len(seat_info)} seats freed)"
            )
            
            return Response({
                'message': 'Booking cancelled successfully',
                'refunded_seats': seat_info
            }, status=status.HTTP_200_OK)
            
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found or you don't have permission to cancel it"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error cancelling booking: {e}")
            return Response(
                {"error": "Failed to cancel booking"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# utility views can be added here as needed

class MovieShowingsView(APIView):
    '''
    lists all showings for a specific movie.

    purpose is user can view all showtimes for the selected movie.

    GET /api/user/movies/<movie_id>/showings/

    Response:
    {
        "movie": {
            "movie_id": 5,
            "movie_title": "Inception",
            "poster_url": "https://..."
        },
        "showings": [
            {
                "showing_id": 42,
                "showroom_name": "Theater 1",
                "start_time": "2025-11-15T19:30:00Z",
                "available_seats": 95
            },
            ...
        ]
    }
    '''
    permission_classes = []

    def get(self, request, movie_id):
        """Get all showings for a movie"""
        try:
            # this checks to see if the movie exists
            movie = Movie.objects.get(movie_id=movie_id)
            
            # looks up the future showings for that movie
            showings = Showing.objects.filter(
                movie_id=movie_id,
                start_time__gte=timezone.now()
            ).select_related('showroom').order_by('start_time')
            
            # serialize showings
            serializer = ShowingDetailSerializer(showings, many=True)
            
            return Response({
                'movie': {
                    'movie_id': movie.movie_id,
                    'movie_title': movie.movie_title,
                    'poster_url': movie.poster_url
                },
                'showings': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error listing movie showings: {e}")
            return Response(
                {"error": "Failed to retrieve movie showings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )