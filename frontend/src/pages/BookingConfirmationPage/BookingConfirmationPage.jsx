import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";
import { getBooking } from "../../api";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";

const BookingConfirmationPage = () => {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBookingDetails = async () => {
      try {
        const data = await getBooking(bookingId);
        setBooking(data);
      } catch (err) {
        console.error("Error fetching booking details:", err);
        setError("Failed to load booking confirmation.");
      } finally {
        setLoading(false);
      }
    };

    if (bookingId) {
      fetchBookingDetails();
    }
  }, [bookingId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-xl">Loading confirmation...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center gap-4">
        <div className="text-red-400 text-xl">{error}</div>
        <button
          onClick={() => navigate("/")}
          className="bg-gray-700 px-6 py-2 rounded-lg hover:bg-gray-600 transition"
        >
          Return Home
        </button>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-900 text-white p-6 flex justify-center">
        <div className="w-full max-w-3xl mt-10">
          {/* Success Banner */}
          <div className="bg-green-600/20 border border-green-500 rounded-xl p-6 text-center mb-8 flex flex-col items-center gap-2">
            <CheckCircleOutlineIcon className="text-green-400 !text-6xl" />
            <h1 className="text-3xl font-bold text-green-400">
              Booking Confirmed!
            </h1>
            <p className="text-gray-300">
              A confirmation email has been sent to{" "}
              <span className="font-semibold text-white">
                {booking.user_email}
              </span>
            </p>
          </div>

          {/* Ticket Receipt */}
          <div className="bg-gray-800 rounded-xl shadow-2xl border border-gray-700 overflow-hidden">
            <div className="p-8 border-b border-gray-700 bg-gray-850">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-3xl font-bold text-white mb-2">
                    {booking.movie_title}
                  </h2>
                  <p className="text-red-300 text-lg font-medium">
                    {booking.showroom_name}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-gray-400 text-sm">Booking ID</p>
                  <p className="font-mono text-xl font-bold text-white">
                    #{booking.booking_id}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex items-center gap-2 text-gray-300">
                <span className="bg-gray-700 px-3 py-1 rounded-md text-sm uppercase tracking-wider font-semibold">
                  Showtime
                </span>
                <span className="text-xl">
                  {new Date(booking.start_time).toLocaleString(undefined, {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </div>

            <div className="p-8">
              <h3 className="text-gray-400 text-sm uppercase tracking-wider font-bold mb-4">
                Tickets
              </h3>
              <div className="space-y-3 mb-8">
                {booking.tickets.map((ticket) => (
                  <div
                    key={ticket.ticket_id}
                    className="flex justify-between items-center bg-gray-700/30 p-3 rounded-lg border border-gray-700"
                  >
                    <div className="flex items-center gap-4">
                      <div className="bg-gray-700 px-3 py-2 rounded text-center min-w-[3rem]">
                        <span className="text-xs text-gray-400 block">
                          Seat
                        </span>
                        <span className="font-bold text-white">
                          {ticket.seat_display}
                        </span>
                      </div>
                      <span className="text-gray-200">
                        {ticket.age_category} Ticket
                      </span>
                    </div>
                    <span className="font-mono text-gray-300">
                      ${ticket.price}
                    </span>
                  </div>
                ))}
              </div>

              <div className="border-t border-gray-700 pt-6 flex justify-between items-end">
                <div className="text-gray-400 text-sm">
                  Booked on{" "}
                  {new Date(booking.booking_time).toLocaleDateString()}
                </div>
                <div className="text-right">
                  <p className="text-gray-400 mb-1">Total Paid</p>
                  <p className="text-4xl font-bold text-green-400">
                    ${booking.total_price}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mt-8 justify-center">
            <button
              onClick={() => navigate("/")}
              className="px-8 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors"
            >
              Back to Home
            </button>
            <button
              onClick={() => navigate("/order-history")}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
            >
              View Order History
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default BookingConfirmationPage;
