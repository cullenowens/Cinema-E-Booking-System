import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";
import {
  getMovieDetails,
  getUserMovieShowings,
  getShowingSeats,
  getPaymentCards,
  previewBooking,
  createBooking,
} from "../../api";

const BookingPage = () => {
  const { id, showtime } = useParams();
  const navigate = useNavigate();

  const [movie, setMovie] = useState(null);
  const [showing, setShowing] = useState(null);
  const [seatMap, setSeatMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Ticket Selection States
  const [tickets, setTickets] = useState({
    Adult: 0,
    Child: 0,
    Senior: 0,
  });

  // Seat Selection State
  const [selectedSeats, setSelectedSeats] = useState([]);

  // Checkout Modal States
  const [showCheckout, setShowCheckout] = useState(false);
  const [paymentCards, setPaymentCards] = useState([]);
  const [selectedCardId, setSelectedCardId] = useState("");
  const [useNewCard, setUseNewCard] = useState(false);
  const [promoCode, setPromoCode] = useState("");
  const [previewData, setPreviewData] = useState(null);

  // Updated to include CVV
  const [newCardData, setNewCardData] = useState({
    cardNumber: "",
    expiration: "",
    cvv: "", // Added CVV here
    brand: "",
  });

  const decodedShowtime = decodeURIComponent(showtime);
  const totalTickets = tickets.Adult + tickets.Child + tickets.Senior;
  const seatsRemaining = totalTickets - selectedSeats.length;

  // Fetch Movie, Showing, and Seat Data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        const movieData = await getMovieDetails(id);
        setMovie(movieData);

        const showingsRes = await getUserMovieShowings(id);
        const allShowings = showingsRes.showings || [];

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
      const newTotal = totalTickets - prev[category] + newVal;
      if (newTotal < selectedSeats.length) {
        setSelectedSeats((prevSeats) => prevSeats.slice(0, newTotal));
      }
      return { ...prev, [category]: newVal };
    });
  };

  // Handle Seat Selection
  const handleSeatClick = (seat) => {
    if (!seat.is_available) return;

    const isSelected = selectedSeats.includes(seat.seat_id);

    if (isSelected) {
      setSelectedSeats((prev) => prev.filter((id) => id !== seat.seat_id));
    } else {
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

  // Helper: Construct seats payload with age categories
  const constructSeatsPayload = () => {
    const ticketTypes = [];
    Object.entries(tickets).forEach(([type, count]) => {
      for (let i = 0; i < count; i++) {
        ticketTypes.push(type);
      }
    });

    return selectedSeats.map((seatId, index) => ({
      seat_id: seatId,
      age_category: ticketTypes[index] || "Adult",
    }));
  };

  // Open Checkout Modal
  const handleProceedToCheckout = async () => {
    if (selectedSeats.length !== totalTickets || totalTickets === 0) {
      alert("Please select seats for all your tickets.");
      return;
    }

    setShowCheckout(true);
    try {
      const cards = await getPaymentCards();
      setPaymentCards(cards);
      if (cards.length > 0) {
        setSelectedCardId(cards[0].id);
      } else {
        setUseNewCard(true);
      }
    } catch (err) {
      console.error("Failed to fetch payment cards", err);
    }

    await updatePreview();
  };

  const updatePreview = async (code = "") => {
    try {
      const payload = {
        showing_id: showing.showing_id,
        seats: constructSeatsPayload(),
        promo_code: code || promoCode,
      };
      const data = await previewBooking(payload);
      setPreviewData(data);
    } catch (err) {
      console.error("Preview failed", err);
      if (code) alert("Invalid or expired promo code");
    }
  };

  const handleConfirmBooking = async () => {
    try {
      const seatsPayload = constructSeatsPayload();
      const bookingPayload = {
        showing_id: showing.showing_id,
        seats: seatsPayload,
        promo_code: promoCode,
      };

      if (useNewCard) {
        // Updated validation to check for CVV
        if (
          !newCardData.cardNumber ||
          !newCardData.expiration ||
          !newCardData.brand ||
          !newCardData.cvv
        ) {
          alert("Please fill in all card details, including CVV.");
          return;
        }
        bookingPayload.card_number = newCardData.cardNumber;
        bookingPayload.expiration = newCardData.expiration;
        bookingPayload.brand = newCardData.brand;
        bookingPayload.cvv = newCardData.cvv; // Passed to backend
      } else {
        if (!selectedCardId) {
          alert("Please select a payment card.");
          return;
        }
        bookingPayload.payment_card_id = selectedCardId;
      }

      const res = await createBooking(bookingPayload);
      alert("Booking confirmed! Check your email.");
      if (res && res.booking_id) {
        navigate(`/booking-confirmation/${res.booking_id}`);
      }
    } catch (err) {
      console.error("Booking failed", err);
      const msg =
        err.response?.data?.error || "Booking failed. Please try again.";
      alert(msg);
    }
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
    <div className="min-h-screen bg-gray-900 text-white relative">
      <Navbar />

      <div className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LEFT COLUMN */}
        <div className="lg:col-span-1 space-y-6">
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

        {/* RIGHT COLUMN */}
        <div className="lg:col-span-2 space-y-6">
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
                          "bg-gray-600 hover:bg-gray-500 cursor-pointer border-gray-500";
                        if (!isAvailable)
                          seatClasses =
                            "bg-gray-900 cursor-not-allowed text-gray-700 border-gray-800";
                        if (isSelected)
                          seatClasses =
                            "bg-green-500 text-white border-green-400 shadow-[0_0_10px_rgba(34,197,94,0.5)] transform scale-110";

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

          <div className="flex justify-end">
            <button
              onClick={handleProceedToCheckout}
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

      {/* CHECKOUT MODAL */}
      {showCheckout && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 p-4 overflow-y-auto">
          <div className="bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl border border-gray-700">
            <div className="p-6 border-b border-gray-700 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">Checkout</h2>
              <button
                onClick={() => setShowCheckout(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Order Summary */}
              <div>
                <h3 className="text-lg font-semibold text-red-300 mb-3">
                  Order Summary
                </h3>
                <div className="bg-gray-700/50 rounded-lg p-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Movie:</span>
                    <span className="text-white font-medium">
                      {movie.movie_title}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Tickets:</span>
                    <span className="text-white">
                      {tickets.Adult} Adult, {tickets.Child} Child,{" "}
                      {tickets.Senior} Senior
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Seats:</span>
                    <span className="text-white">
                      {previewData?.seats
                        ?.map((s) => s.seat_display)
                        .join(", ") || "Loading..."}
                    </span>
                  </div>
                  <div className="pt-2 mt-2 border-t border-gray-600 flex justify-between">
                    <span>Base Price:</span>
                    <span>{previewData?.base_price}</span>
                  </div>
                  {previewData?.discount_amount && (
                    <div className="flex justify-between text-green-400">
                      <span>Discount ({previewData.promotion_applied}):</span>
                      <span>{previewData.discount_display}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-xl font-bold text-white pt-2">
                    <span>Total:</span>
                    <span>{previewData?.final_price}</span>
                  </div>
                </div>
              </div>

              {/* Promo Code */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Promo Code
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={promoCode}
                    onChange={(e) => setPromoCode(e.target.value)}
                    className="flex-1 px-4 py-2 bg-gray-700 rounded-lg text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Enter code"
                  />
                  <button
                    onClick={() => updatePreview(promoCode)}
                    className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white transition-colors"
                  >
                    Apply
                  </button>
                </div>
              </div>

              {/* Payment Method */}
              <div>
                <h3 className="text-lg font-semibold text-red-300 mb-3">
                  Payment Method
                </h3>

                {paymentCards.length > 0 && (
                  <div className="flex gap-4 mb-4">
                    <button
                      onClick={() => setUseNewCard(false)}
                      className={`flex-1 py-2 rounded-lg transition-colors ${
                        !useNewCard
                          ? "bg-red-500 text-white"
                          : "bg-gray-700 text-gray-400 hover:bg-gray-600"
                      }`}
                    >
                      Saved Card
                    </button>
                    <button
                      onClick={() => setUseNewCard(true)}
                      className={`flex-1 py-2 rounded-lg transition-colors ${
                        useNewCard
                          ? "bg-red-500 text-white"
                          : "bg-gray-700 text-gray-400 hover:bg-gray-600"
                      }`}
                    >
                      New Card
                    </button>
                  </div>
                )}

                {!useNewCard && paymentCards.length > 0 ? (
                  <select
                    value={selectedCardId}
                    onChange={(e) => setSelectedCardId(e.target.value)}
                    className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white border border-gray-600 focus:ring-2 focus:ring-red-500"
                  >
                    {paymentCards.map((card) => (
                      <option key={card.id} value={card.id}>
                        {card.brand} ending in{" "}
                        {card.card_number_enc
                          ? "****" + card.card_number_enc.slice(-4)
                          : "****"}{" "}
                        (Exp: {card.expiration})
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="Card Number"
                      className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white border border-gray-600"
                      value={newCardData.cardNumber}
                      maxLength="19"
                      onChange={(e) =>
                        setNewCardData({
                          ...newCardData,
                          cardNumber: e.target.value.replace(/\D/g, ""),
                        })
                      }
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="MM/YYYY"
                        className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white border border-gray-600"
                        value={newCardData.expiration}
                        maxLength="7"
                        onChange={(e) =>
                          setNewCardData({
                            ...newCardData,
                            expiration: e.target.value,
                          })
                        }
                      />
                      {/* Added CVV Input Field Here */}
                      <input
                        type="text"
                        placeholder="CVV"
                        className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white border border-gray-600"
                        value={newCardData.cvv}
                        maxLength="4"
                        onChange={(e) =>
                          setNewCardData({
                            ...newCardData,
                            cvv: e.target.value.replace(/\D/g, ""),
                          })
                        }
                      />
                    </div>
                    <input
                      type="text"
                      placeholder="Brand (Visa, MasterCard)"
                      className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white border border-gray-600"
                      value={newCardData.brand}
                      onChange={(e) =>
                        setNewCardData({
                          ...newCardData,
                          brand: e.target.value,
                        })
                      }
                    />
                  </div>
                )}
              </div>
            </div>

            <div className="p-6 border-t border-gray-700 flex gap-4">
              <button
                onClick={() => setShowCheckout(false)}
                className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Back
              </button>
              <button
                onClick={handleConfirmBooking}
                className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg transition-colors shadow-lg"
              >
                Confirm & Pay
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BookingPage;
