import React, { useEffect, useState } from "react";
import Navbar from "../../components/Navbar/Navbar";
import { getBookings } from "../../api";

const OrderHistoryPage = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getBookings();
        setBookings(data.bookings || []);
      } catch (error) {
        console.error("Error fetching order history:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 text-red-300">
            Order History
          </h1>

          {loading ? (
            <div className="text-center text-gray-400">Loading orders...</div>
          ) : bookings.length === 0 ? (
            <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
              <p className="text-gray-400 text-lg">
                You haven't made any bookings yet.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {bookings.map((booking) => (
                <div
                  key={booking.booking_id}
                  className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 shadow-lg hover:border-gray-600 transition-colors"
                >
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h2 className="text-2xl font-bold text-white mb-1">
                          {booking.movie_title}
                        </h2>
                        <p className="text-gray-400 text-sm">
                          {booking.showroom_name}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-red-300 font-bold text-xl">
                          ${booking.total_price}
                        </p>
                        <p className="text-gray-500 text-xs mt-1">
                          Booking #{booking.booking_id}
                        </p>
                      </div>
                    </div>

                    <div className="border-t border-gray-700 pt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-500 text-sm mb-1 uppercase tracking-wider">
                          Showtime
                        </p>
                        <p className="text-white font-medium">
                          {new Date(booking.start_time).toLocaleDateString(
                            undefined,
                            {
                              weekday: "long",
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            }
                          )}
                        </p>
                        <p className="text-white">
                          {new Date(booking.start_time).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </p>
                      </div>

                      <div>
                        <p className="text-gray-500 text-sm mb-1 uppercase tracking-wider">
                          Tickets
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {booking.tickets.map((ticket) => (
                            <span
                              key={ticket.ticket_id}
                              className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300 border border-gray-600"
                            >
                              {ticket.seat_display} ({ticket.age_category})
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-700/30 px-6 py-3 border-t border-gray-700">
                    <p className="text-gray-500 text-xs">
                      Booked on{" "}
                      {new Date(booking.booking_time).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default OrderHistoryPage;
