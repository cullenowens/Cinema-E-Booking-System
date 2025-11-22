import React, { useState, useEffect } from "react";
import Navbar from "../../components/Navbar/Navbar";
import {
  getPromotions,
  createPromotion,
  deletePromotion,
  sendPromotionEmail,
} from "../../api";

const ManagePromotionsPage = () => {
  // Data State
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [sendingEmailId, setSendingEmailId] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    promo_code: "",
    discount: "",
    start_date: "",
    end_date: "",
    send_email: false, // Checkbox for immediate email
  });

  const [errors, setErrors] = useState({});
  const [notification, setNotification] = useState({ type: "", message: "" });

  // Fetch Data
  const fetchPromotions = async () => {
    try {
      setLoading(true);
      const data = await getPromotions();
      setPromotions(data.promotions || []);
    } catch (error) {
      console.error("Error fetching promotions:", error);
      setNotification({ type: "error", message: "Failed to load promotions." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPromotions();
  }, []);

  // Handlers
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.promo_code.trim())
      newErrors.promo_code = "Promo Code is required";
    if (!formData.discount) newErrors.discount = "Discount is required";
    else if (formData.discount <= 0 || formData.discount > 100)
      newErrors.discount = "Discount must be between 1% and 100%";
    if (!formData.start_date) newErrors.start_date = "Start Date is required";
    if (!formData.end_date) newErrors.end_date = "End Date is required";

    if (formData.start_date && formData.end_date) {
      if (new Date(formData.end_date) <= new Date(formData.start_date)) {
        newErrors.end_date = "End Date must be after Start Date";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = async () => {
    if (!validateForm()) return;

    try {
      const payload = {
        promo_code: formData.promo_code,
        discount: parseFloat(formData.discount),
        start_date: formData.start_date,
        end_date: formData.end_date,
        send_email: formData.send_email,
      };

      const res = await createPromotion(payload);

      let successMsg = "Promotion created successfully!";
      if (res.emails_sent > 0) {
        successMsg += ` Email sent to ${res.emails_sent} subscribers.`;
      }

      setNotification({ type: "success", message: successMsg });
      setShowModal(false);
      setFormData({
        promo_code: "",
        discount: "",
        start_date: "",
        end_date: "",
        send_email: false,
      });
      fetchPromotions();
    } catch (error) {
      console.error("Create error:", error);
      const msg = error.response?.data?.error || "Failed to create promotion.";
      setNotification({ type: "error", message: msg });

      // Map backend validation errors if available
      if (error.response?.data?.details) {
        setErrors(error.response.data.details);
      }
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this promotion?"))
      return;
    try {
      await deletePromotion(id);
      setNotification({ type: "success", message: "Promotion deleted." });
      setPromotions(promotions.filter((p) => p.promo_id !== id));
    } catch (error) {
      setNotification({
        type: "error",
        message: "Failed to delete promotion.",
      });
    }
  };

  const handleSendEmail = async (id) => {
    if (!window.confirm("Send this promotion to all subscribed users?")) return;

    setSendingEmailId(id);
    try {
      const res = await sendPromotionEmail(id);
      setNotification({
        type: "success",
        message: `Email sent successfully to ${res.emails_sent} users.`,
      });
    } catch (error) {
      console.error("Email error:", error);
      setNotification({ type: "error", message: "Failed to send emails." });
    } finally {
      setSendingEmailId(null);
    }
  };

  // Helper to format percentage
  const formatPercent = (val) => {
    // remove trailing zeros
    return parseFloat(val) + "%";
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-red-300">
              Manage Promotions
            </h1>
            <button
              onClick={() => {
                setErrors({});
                setNotification({ type: "", message: "" });
                setShowModal(true);
              }}
              className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <span className="text-xl">+</span> Add Promotion
            </button>
          </div>

          {/* Notifications */}
          {notification.message && (
            <div
              className={`mb-6 p-4 rounded-lg border ${
                notification.type === "success"
                  ? "bg-green-900/50 border-green-500 text-green-200"
                  : "bg-red-900/50 border-red-500 text-red-200"
              }`}
            >
              {notification.message}
            </div>
          )}

          {/* Promotions Table */}
          <div className="bg-gray-800 rounded-lg overflow-hidden shadow-xl border border-gray-700">
            {loading ? (
              <div className="p-8 text-center text-gray-400">Loading...</div>
            ) : promotions.length === 0 ? (
              <div className="p-8 text-center text-gray-400">
                No promotions found. Create one to get started!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="bg-gray-700 text-gray-300 uppercase text-sm">
                    <tr>
                      <th className="p-4">Promo Code</th>
                      <th className="p-4">Discount</th>
                      <th className="p-4">Start Date</th>
                      <th className="p-4">End Date</th>
                      <th className="p-4 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {promotions.map((promo) => (
                      <tr
                        key={promo.promo_id}
                        className="hover:bg-gray-750 transition-colors"
                      >
                        <td className="p-4 font-mono font-bold text-yellow-400">
                          {promo.promo_code}
                        </td>
                        <td className="p-4 font-semibold">
                          {formatPercent(promo.discount)}
                        </td>
                        <td className="p-4 text-gray-300">
                          {promo.start_date}
                        </td>
                        <td className="p-4 text-gray-300">{promo.end_date}</td>
                        <td className="p-4 flex justify-center gap-3">
                          <button
                            onClick={() => handleSendEmail(promo.promo_id)}
                            disabled={sendingEmailId === promo.promo_id}
                            className="bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 px-3 py-1 rounded text-sm transition-colors border border-blue-500/50"
                          >
                            {sendingEmailId === promo.promo_id
                              ? "Sending..."
                              : "Email Users"}
                          </button>
                          <button
                            onClick={() => handleDelete(promo.promo_id)}
                            className="text-red-400 hover:text-red-300 font-medium transition-colors text-sm"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Create Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg w-full max-w-md shadow-2xl border border-gray-700">
              <div className="flex justify-between items-center p-6 border-b border-gray-700">
                <h2 className="text-2xl font-bold text-white">New Promotion</h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 space-y-4">
                {/* Promo Code */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Promo Code *
                  </label>
                  <input
                    type="text"
                    name="promo_code"
                    value={formData.promo_code}
                    onChange={handleInputChange}
                    placeholder="e.g. SUMMER2025"
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600 uppercase"
                  />
                  {errors.promo_code && (
                    <p className="text-red-400 text-sm mt-1">
                      {errors.promo_code}
                    </p>
                  )}
                </div>

                {/* Discount */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Discount Percentage (%) *
                  </label>
                  <input
                    type="number"
                    name="discount"
                    value={formData.discount}
                    onChange={handleInputChange}
                    placeholder="20"
                    min="1"
                    max="100"
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600"
                  />
                  {errors.discount && (
                    <p className="text-red-400 text-sm mt-1">
                      {errors.discount}
                    </p>
                  )}
                </div>

                {/* Dates Row */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Start Date *
                    </label>
                    <input
                      type="date"
                      name="start_date"
                      value={formData.start_date}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600"
                    />
                    {errors.start_date && (
                      <p className="text-red-400 text-sm mt-1">
                        {errors.start_date}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      End Date *
                    </label>
                    <input
                      type="date"
                      name="end_date"
                      value={formData.end_date}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600"
                    />
                    {errors.end_date && (
                      <p className="text-red-400 text-sm mt-1">
                        {errors.end_date}
                      </p>
                    )}
                  </div>
                </div>

                {/* Send Email Checkbox */}
                <div className="pt-2">
                  <label className="flex items-center space-x-3 cursor-pointer p-3 bg-gray-700/50 rounded-lg border border-gray-600 hover:bg-gray-700 transition">
                    <input
                      type="checkbox"
                      name="send_email"
                      checked={formData.send_email}
                      onChange={handleInputChange}
                      className="w-5 h-5 text-red-500 rounded focus:ring-red-500 bg-gray-800 border-gray-500"
                    />
                    <span className="text-gray-200">
                      Email this promotion to subscribers immediately?
                    </span>
                  </label>
                </div>

                {/* Buttons */}
                <div className="flex gap-4 pt-4">
                  <button
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreate}
                    className="flex-1 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors font-semibold"
                  >
                    Create Promotion
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default ManagePromotionsPage;
