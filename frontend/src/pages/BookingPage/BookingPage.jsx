import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";
import {
  getMovieDetails,
  getUserMovieShowings,
  getShowingSeats,
} from "../../api";

const BookingPage = () => {
  const { id, showtime } = useParams();
  const navigate = useNavigate();

  const [movie, setMovie] = useState(null);
  const [showing, setShowing] = useState(null);
  const [seatMap, setSeatMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 2.3 Ticket Selection States
  const [tickets, setTickets] = useState({
    Adult: 0,
    Child: 0,
    Senior: 0,
  });

  // 2.4 Seat Selection State
  const [selectedSeats, setSelectedSeats] = useState([]);

  const decodedShowtime = decodeURIComponent(showtime);
  const totalTickets = tickets.Adult + tickets.Child + tickets.Senior;
  const seatsRemaining = totalTickets - selectedSeats.length;

  // Fetch Movie, Showing, and Seat Data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // 1. Fetch Movie Details
        const movieData = await getMovieDetails(id);
        setMovie(movieData);

        // 2. Fetch showings to find the matching showing ID from the URL string
        const showingsRes = await getUserMovieShowings(id);
        const allShowings = showingsRes.showings || [];

        // Match the showtime string from URL to a specific showing record
        const matchedShowing = allShowings.find((s) => {
          const sTime = new Date(s.start_time);
          return (
            s.start_time === decodedShowtime ||
            sTime.toLocaleString() === decodedShowtime ||
            sTime.toISOString() === decodedShowtime
          );
        });

        if (matchedShowing) {
          setShowing(matchedShowing);

          // 3. Fetch Seat Map using the centralized API function
          const seatRes = await getShowingSeats(matchedShowing.showing_id);
          setSeatMap(seatRes.seats_by_row || {});
        } else {
          setError("Showtime not found. Please return to the movie page.");
        }
      } catch (err) {
        console.error("Error loading booking data:", err);
        setError("Failed to load booking data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchData();
  }, [id, decodedShowtime]);

  // Handle Ticket Count Changes
  const handleTicketChange = (category, change) => {
    setTickets((prev) => {
      const newVal = Math.max(0, prev[category] + change);

      // If total tickets decrease below selected seats, deselect the most recent ones
      // This ensures 2.4 constraints are met (seats selected <= tickets)
      const newTotal = totalTickets - prev[category] + newVal;
      if (newTotal < selectedSeats.length) {
        setSelectedSeats((prevSeats) => prevSeats.slice(0, newTotal));
      }

      return { ...prev, [category]: newVal };
    });
  };

  // Handle Seat Selection (2.4)
  const handleSeatClick = (seat) => {
    // System enforces availability
    if (!seat.is_available) return;

    const isSelected = selectedSeats.includes(seat.seat_id);

    if (isSelected) {
      // Deselect
      setSelectedSeats((prev) => prev.filter((id) => id !== seat.seat_id));
    } else {
      // Select: System prevents invalid selections (more seats than tickets)
      if (selectedSeats.length < totalTickets) {
        setSelectedSeats((prev) => [...prev, seat.seat_id]);
      } else {
        if (totalTickets === 0) {
          alert("Please add tickets before selecting seats.");
        } else {
          alert(
            `You have already selected ${totalTickets} seats for your ${totalTickets} tickets.`
          );
        }
      }
    }
  };

  const handleCheckout = () => {
    if (selectedSeats.length !== totalTickets || totalTickets === 0) {
      alert("Please select seats for all your tickets.");
      return;
    }
    // Checkout logic not implemented yet per requirements
    alert("Proceeding to checkout...");
  };

  if (loading)
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8 text-center">
        Loading...
      </div>
    );
  if (error)
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8 text-center text-red-400">
        {error}
      </div>
    );
  if (!movie || !showing) return null;

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar />

      <div className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LEFT COLUMN: Movie Info & Ticket Selection */}
        <div className="lg:col-span-1 space-y-6">
          {/* Movie Info Card */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
            <h1 className="text-2xl font-bold mb-2 text-white">
              {movie.movie_title}
            </h1>
            <div className="text-gray-300 text-sm mb-4 space-y-1">
              <p>
                {new Date(showing.start_time).toLocaleDateString(undefined, {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
              <p className="text-red-300 font-semibold">
                {new Date(showing.start_time).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
              <p>Theater: {showing.showroom_name}</p>
            </div>
            <div className="aspect-[2/3] w-full rounded-lg overflow-hidden mb-4 shadow-md">
              <img
                src={movie.poster_url}
                alt={movie.movie_title}
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* 2.3 Ticket Category Selection */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-lg">
            <h2 className="text-xl font-bold mb-4 text-red-300 border-b border-gray-700 pb-2">
              Select Tickets
            </h2>
            <div className="space-y-4">
              {Object.keys(tickets).map((type) => (
                <div key={type} className="flex justify-between items-center">
                  <span className="capitalize font-medium">{type}</span>
                  <div className="flex items-center bg-gray-700 rounded-lg overflow-hidden border border-gray-600">
                    <button
                      onClick={() => handleTicketChange(type, -1)}
                      className="px-3 py-2 hover:bg-gray-600 text-red-300 font-bold transition-colors"
                      disabled={tickets[type] <= 0}
                    >
                      −
                    </button>
                    <span className="px-3 w-8 text-center font-mono">
                      {tickets[type]}
                    </span>
                    <button
                      onClick={() => handleTicketChange(type, 1)}
                      className="px-3 py-2 hover:bg-gray-600 text-green-300 font-bold transition-colors"
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 pt-4 border-t border-gray-700 flex justify-between font-bold text-lg">
              <span>Total Tickets</span>
              <span className="text-red-300">{totalTickets}</span>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Seat Map & Selection */}
        <div className="lg:col-span-2 space-y-6">
          {/* 2.3 & 2.4 Seat Selection Interface */}
          <div className="bg-gray-800 rounded-xl p-8 border border-gray-700 shadow-lg min-h-[600px] flex flex-col">
            <h2 className="text-2xl font-bold mb-2 text-center">
              Select Seats
            </h2>
            <p className="text-center text-gray-400 mb-8 h-6">
              {totalTickets > 0 ? (
                seatsRemaining > 0 ? (
                  `Please select ${seatsRemaining} more seat${
                    seatsRemaining !== 1 ? "s" : ""
                  }`
                ) : (
                  <span className="text-green-400 font-medium">
                    All seats selected! Ready for checkout.
                  </span>
                )
              ) : (
                "Start by adding tickets on the left"
              )}
            </p>

            {/* Screen Visual */}
            <div className="w-3/4 mx-auto h-2 bg-gray-600 rounded-full mb-12 shadow-[0_0_15px_rgba(255,255,255,0.2)] relative">
              <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-xs text-gray-500 uppercase tracking-[0.3em]">
                Screen
              </span>
            </div>

            {/* Seat Grid */}
            <div className="flex-1 flex flex-col items-center justify-start gap-3 overflow-x-auto py-4">
              {Object.keys(seatMap)
                .sort()
                .map((rowLabel) => (
                  <div key={rowLabel} className="flex gap-4 items-center">
                    <span className="w-4 text-right text-gray-500 font-mono font-bold">
                      {rowLabel}
                    </span>
                    <div className="flex gap-2">
                      {seatMap[rowLabel].map((seat) => {
                        const isSelected = selectedSeats.includes(seat.seat_id);
                        const isAvailable = seat.is_available;

                        let seatClasses =
                          "bg-gray-600 hover:bg-gray-500 cursor-pointer border-gray-500"; // Default Available
                        if (!isAvailable)
                          seatClasses =
                            "bg-gray-900 cursor-not-allowed text-gray-700 border-gray-800"; // Occupied
                        if (isSelected)
                          seatClasses =
                            "bg-green-500 text-white border-green-400 shadow-[0_0_10px_rgba(34,197,94,0.5)] transform scale-110"; // Selected

                        return (
                          <button
                            key={seat.seat_id}
                            onClick={() => handleSeatClick(seat)}
                            disabled={!isAvailable}
                            className={`w-8 h-8 rounded-t-lg border-b-2 text-[10px] flex items-center justify-center transition-all duration-200 ${seatClasses}`}
                            title={`${rowLabel}${seat.seat_number} - ${
                              isAvailable ? "Available" : "Occupied"
                            }`}
                          >
                            {seat.seat_number}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
            </div>

            {/* Legend */}
            <div className="flex justify-center gap-8 mt-8 text-sm text-gray-400 border-t border-gray-700 pt-6">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 bg-gray-600 rounded-t-sm"></div>
                <span>Available</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 bg-green-500 rounded-t-sm"></div>
                <span>Selected</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 bg-gray-900 rounded-t-sm border border-gray-700"></div>
                <span>Occupied</span>
              </div>
            </div>
          </div>

          {/* Checkout Button */}
          <div className="flex justify-end">
            <button
              onClick={handleCheckout}
              disabled={
                totalTickets === 0 || selectedSeats.length !== totalTickets
              }
              className={`px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-lg ${
                totalTickets > 0 && selectedSeats.length === totalTickets
                  ? "bg-red-600 hover:bg-red-500 text-white hover:shadow-red-900/20 transform hover:-translate-y-1"
                  : "bg-gray-700 text-gray-500 cursor-not-allowed"
              }`}
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingPage;
