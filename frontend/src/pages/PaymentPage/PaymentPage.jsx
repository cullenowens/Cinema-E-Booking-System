import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";
import { useAuth } from "../../contexts/AuthContext";
import { getPaymentCards, addPaymentCard, deletePaymentCard } from "../../api";

const PaymentPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [view, setView] = useState("list"); // 'list' or 'add'
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);

  const [formData, setFormData] = useState({
    brand: "",
    cardNumber: "",
    expiration: "",
    cvv: "",
    billingZip: "",
  });

  const MAX_CARDS = 4;

  // Load cards from backend
  useEffect(() => {
    const fetchCards = async () => {
      try {
        const data = await getPaymentCards();
        setCards(data);
      } catch (err) {
        console.error("Error fetching cards:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCards();
  }, [user]);

  const handleAddCard = async (e) => {
    e.preventDefault();

    if (formData.cardNumber.length < 13) {
      alert("Please enter a valid card number");
      return;
    }

    try {
      const payload = {
        brand: formData.brand,
        card_number: formData.cardNumber,
        expiration: formData.expiration,
        cvv: formData.cvv,
        billing_zip: formData.billingZip,
      };

      const newCard = await addPaymentCard(payload);
      setCards([...cards, newCard]);

      setFormData({
        brand: "",
        cardNumber: "",
        expiration: "",
        cvv: "",
        billingZip: "",
      });

      setView("list");
    } catch (err) {
      console.log(err.response?.data);
    }
  };

  const handleRemoveCard = async (id) => {
    try {
      await deletePaymentCard(id);
      setCards(cards.filter((card) => card.id !== id));
    } catch (err) {
      console.error("Error deleting card:", err);
      alert("Failed to remove card. Please try again.");
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"></div>
      </>
    );
  }

  if (view === "add") {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
          <div className="max-w-2xl mx-auto">
            <button
              onClick={() => setView("list")}
              className="text-gray-400 hover:text-white mb-6 transition-colors"
            >
              ← Back to Payment Methods
            </button>

            <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700">
              <h1 className="text-3xl font-bold text-white mb-2">
                Add Payment Method
              </h1>
              <p className="text-gray-400 mb-8">Enter your card information</p>

              <form onSubmit={handleAddCard} className="space-y-5">
                <div>
                  <label className="block text-gray-300 mb-2 font-medium">
                    Card Brand
                  </label>
                  <input
                    type="text"
                    value={formData.brand}
                    onChange={(e) =>
                      setFormData({ ...formData, brand: e.target.value })
                    }
                    placeholder="Visa, Mastercard, AMEX, etc."
                    required
                    className="w-full p-4 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2 font-medium">
                    Card Number
                  </label>
                  <input
                    type="text"
                    value={formData.cardNumber}
                    onChange={(e) => {
                      const value = e.target.value
                        .replace(/\D/g, "")
                        .substring(0, 16);
                      setFormData({ ...formData, cardNumber: value });
                    }}
                    placeholder="1234567890123456"
                    maxLength="16"
                    required
                    className="w-full p-4 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 mb-2 font-medium text-sm">
                      Expiration (MM/YY)
                    </label>
                    <input
                      type="text"
                      value={formData.expiration}
                      onChange={(e) => {
                        const value = e.target.value
                          .replace(/[^\d/]/g, "")
                          .substring(0, 7);
                        setFormData({ ...formData, expiration: value });
                      }}
                      placeholder="03/2026"
                      required
                      className="w-full p-4 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-300 mb-2 font-medium text-sm">
                      CVV
                    </label>
                    <input
                      type="text"
                      value={formData.cvv}
                      onChange={(e) => {
                        const value = e.target.value
                          .replace(/\D/g, "")
                          .substring(0, 4);
                        setFormData({ ...formData, cvv: value });
                      }}
                      placeholder="123"
                      maxLength="4"
                      required
                      className="w-full p-4 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2 font-medium">
                    Billing ZIP Code
                  </label>
                  <input
                    type="text"
                    value={formData.billingZip}
                    onChange={(e) => {
                      const value = e.target.value
                        .replace(/\D/g, "")
                        .substring(0, 5);
                      setFormData({ ...formData, billingZip: value });
                    }}
                    placeholder="12345"
                    maxLength="5"
                    required
                    className="w-full p-4 rounded-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="flex gap-4 mt-8">
                  <button
                    type="button"
                    onClick={() => setView("list")}
                    className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-4 rounded-lg font-semibold transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-lg font-semibold transition-all"
                  >
                    Save Card
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Payment Methods
              </h1>
              <p className="text-gray-400">Manage your saved cards</p>
            </div>
            {cards.length < MAX_CARDS && (
              <button
                onClick={() => setView("add")}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-all"
              >
                Add Card
              </button>
            )}
          </div>

          {cards.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-2xl p-12 text-center">
              <h2 className="text-xl text-gray-400 mb-4">
                No payment methods saved
              </h2>
              <button
                onClick={() => setView("add")}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-all"
              >
                Add Your First Card
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {cards.map((card) => (
                <div
                  key={card.id}
                  className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-4 rounded-lg">
                      <svg
                        className="w-8 h-8 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <rect
                          x="2"
                          y="5"
                          width="20"
                          height="14"
                          rx="2"
                          strokeWidth="2"
                        />
                        <line x1="2" y1="10" x2="22" y2="10" strokeWidth="2" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-white font-semibold text-lg">
                        {card.brand} •••• {card.lastFour}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleRemoveCard(card.id)}
                    className="text-red-400 hover:text-red-300 px-4 py-2 transition-colors"
                  >
                    Remove
                  </button>
                </div>
              ))}

              {cards.length >= MAX_CARDS && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 text-center">
                  <p className="text-yellow-400 font-medium">
                    Card limit reached ({MAX_CARDS} cards maximum)
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default PaymentPage;
