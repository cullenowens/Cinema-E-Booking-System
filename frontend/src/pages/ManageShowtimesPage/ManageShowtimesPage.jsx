import React, { useState, useEffect } from "react";
import {
  getAdminShowings,
  getAllMovies, // Using the correct export from index.js
  getAdminShowrooms,
  createShowing,
  updateShowing,
  deleteShowing,
  checkShowingAvailability,
} from "../../api";
import Navbar from "../../components/Navbar/Navbar";

const ManageShowtimesPage = () => {
  // Data States
  const [showings, setShowings] = useState([]);
  const [movies, setMovies] = useState([]);
  const [showrooms, setShowrooms] = useState([]);

  // UI States
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState("add"); // "add" or "edit"
  const [selectedShowing, setSelectedShowing] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    movie_id: "",
    showroom_id: "",
    start_time: "",
    end_time: "",
  });

  const [formErrors, setFormErrors] = useState({});
  const [isCheckingConflict, setIsCheckingConflict] = useState(false);

  // Initial Data Fetch
  useEffect(() => {
    fetchData();
  }, []);

  // Real-time Conflict Check
  useEffect(() => {
    const timer = setTimeout(() => {
      if (formData.showroom_id && formData.start_time && showModal) {
        performConflictCheck();
      }
    }, 500); // Debounce 500ms

    return () => clearTimeout(timer);
  }, [formData.showroom_id, formData.start_time, formData.end_time, showModal]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [showingsData, moviesData, showroomsData] = await Promise.all([
        getAdminShowings(),
        getAllMovies(),
        getAdminShowrooms(),
      ]);

      setShowings(showingsData.showings || []);
      setMovies(moviesData.movies || []);
      setShowrooms(showroomsData.showrooms || []);
    } catch (error) {
      console.error("Error fetching data:", error);
      // Using formErrors for global errors isn't ideal here, but works for now
      // or just console log since user can't do much about load failure
    } finally {
      setLoading(false);
    }
  };

  const performConflictCheck = async () => {
    setIsCheckingConflict(true);
    setFormErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors.conflict;
      delete newErrors.general; // Clear general errors too
      return newErrors;
    });

    try {
      const result = await checkShowingAvailability(
        formData.showroom_id,
        formData.start_time,
        formData.end_time
      );

      if (!result.available) {
        // Filter out the current showing if we are editing
        const realConflicts =
          modalMode === "edit" && selectedShowing
            ? result.conflicts.filter(
                (c) =>
                  new Date(c.start_time).getTime() !==
                  new Date(selectedShowing.start_time).getTime()
              )
            : result.conflicts;

        if (realConflicts && realConflicts.length > 0) {
          const conflictMsg = realConflicts
            .map(
              (c) =>
                `${c.movie_title} (${new Date(
                  c.start_time
                ).toLocaleTimeString()})`
            )
            .join(", ");

          setFormErrors((prev) => ({
            ...prev,
            conflict: `Time slot conflict with: ${conflictMsg}`,
          }));
        }
      }
    } catch (error) {
      console.error("Conflict check failed", error);
    } finally {
      setIsCheckingConflict(false);
    }
  };

  // Modal Handlers
  const handleOpenModal = (mode, showing = null) => {
    setModalMode(mode);
    setFormErrors({});

    if (mode === "edit" && showing) {
      setSelectedShowing(showing);
      setFormData({
        movie_id: showing.movie_id,
        showroom_id: showing.showroom_id,
        start_time: formatForInput(showing.start_time),
        end_time: formatForInput(showing.end_time),
      });
    } else {
      setSelectedShowing(null);
      setFormData({
        movie_id: "",
        showroom_id: "",
        start_time: "",
        end_time: "",
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedShowing(null);
    setFormErrors({});
    setFormData({
      movie_id: "",
      showroom_id: "",
      start_time: "",
      end_time: "",
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear specific error when user types
    if (formErrors[name]) {
      setFormErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    // Clear global errors on input change
    if (formErrors.general || formErrors.conflict) {
      setFormErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors.general;
        // Don't delete conflict here, let performConflictCheck handle it
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.movie_id) errors.movie_id = "Please select a movie";
    if (!formData.showroom_id) errors.showroom_id = "Please select a showroom";
    if (!formData.start_time) errors.start_time = "Start time is required";
    if (formErrors.conflict) errors.conflict = formErrors.conflict;

    setFormErrors((prev) => ({ ...prev, ...errors }));
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    if (formErrors.conflict) return;

    try {
      const payload = {
        movie_id: parseInt(formData.movie_id),
        showroom_id: parseInt(formData.showroom_id),
        start_time: formData.start_time,
        end_time: formData.end_time || null,
      };

      if (modalMode === "add") {
        await createShowing(payload);
        alert("Showtime added successfully!");
      } else {
        await updateShowing(selectedShowing.showing_id, payload);
        alert("Showtime updated successfully!");
      }

      handleCloseModal();
      fetchData();
    } catch (error) {
      console.error("Error saving showing:", error);

      if (error.response?.data) {
        const data = error.response.data;

        // Check 'details' first (custom admin view wrapper), otherwise use data directly
        const details = data.details || data;
        const newErrors = {};

        if (typeof details === "object" && details !== null) {
          // Map backend field errors to frontend state
          Object.keys(details).forEach((key) => {
            // Skip the generic "Validation failed" message if it appears as a key
            if (key === "error" && details[key] === "Validation failed") return;

            const message = Array.isArray(details[key])
              ? details[key][0]
              : details[key];
            newErrors[key] = message;
          });
        }

        // If we didn't find specific field errors, but there's a top-level error message
        if (
          Object.keys(newErrors).length === 0 &&
          data.error &&
          data.error !== "Validation failed"
        ) {
          newErrors.general = data.error;
        }

        // Fallback if absolutely no specific error information was found
        if (Object.keys(newErrors).length === 0) {
          newErrors.general =
            "Validation failed. Please check your inputs and try again.";
        }

        setFormErrors(newErrors);
      } else {
        setFormErrors({ general: "An unexpected server error occurred." });
      }
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this showtime?"))
      return;

    try {
      await deleteShowing(id);
      alert("Showtime deleted successfully!");
      fetchData();
    } catch (error) {
      console.error("Error deleting showing:", error);
      alert(error.response?.data?.error || "Failed to delete showtime");
    }
  };

  // Helpers
  const formatForInput = (isoString) => {
    if (!isoString) return "";
    return new Date(isoString).toISOString().slice(0, 16);
  };

  const formatDateDisplay = (isoString) => {
    return new Date(isoString).toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const filteredShowings = showings.filter(
    (showing) =>
      showing.movie_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      showing.showroom_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-red-300">
              Manage Showtimes
            </h1>
            <button
              onClick={() => handleOpenModal("add")}
              className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <span className="text-xl">+</span>
              Schedule Showing
            </button>
          </div>

          {/* Search Bar */}
          <div className="mb-6 relative">
            <svg
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search by movie or showroom..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-gray-800 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>

          {/* Showings Table */}
          <div className="bg-gray-800 rounded-lg overflow-hidden shadow-xl border border-gray-700">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-gray-700 text-gray-300 uppercase text-sm">
                  <tr>
                    <th className="p-4">Movie</th>
                    <th className="p-4">Showroom</th>
                    <th className="p-4">Start Time</th>
                    <th className="p-4">End Time</th>
                    <th className="p-4 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {filteredShowings.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="p-8 text-center text-gray-400">
                        No showtimes found matching your search.
                      </td>
                    </tr>
                  ) : (
                    filteredShowings.map((showing) => (
                      <tr
                        key={showing.showing_id}
                        className="hover:bg-gray-750 transition-colors"
                      >
                        <td className="p-4 font-semibold">
                          {showing.movie_title}
                        </td>
                        <td className="p-4 text-gray-300">
                          {showing.showroom_name}
                        </td>
                        <td className="p-4 text-gray-300">
                          {formatDateDisplay(showing.start_time)}
                        </td>
                        <td className="p-4 text-gray-300">
                          {showing.end_time
                            ? formatDateDisplay(showing.end_time)
                            : "-"}
                        </td>
                        <td className="p-4 flex justify-center gap-3">
                          <button
                            onClick={() => handleOpenModal("edit", showing)}
                            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(showing.showing_id)}
                            className="text-red-400 hover:text-red-300 font-medium transition-colors"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg w-full max-w-md shadow-2xl border border-gray-700">
              <div className="flex justify-between items-center p-6 border-b border-gray-700">
                <h2 className="text-2xl font-bold text-white">
                  {modalMode === "add" ? "Schedule Showing" : "Edit Showing"}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 space-y-4">
                {/* Global Error Alert (Includes Conflicts) */}
                {(formErrors.conflict || formErrors.general) && (
                  <div className="bg-red-900/50 border border-red-500 text-red-200 p-3 rounded-lg text-sm">
                    <strong>Error:</strong>{" "}
                    {formErrors.conflict || formErrors.general}
                  </div>
                )}

                {/* Movie Select */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Movie *
                  </label>
                  <select
                    name="movie_id"
                    value={formData.movie_id}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600"
                  >
                    <option value="">Select a Movie</option>
                    {movies.map((m) => (
                      <option key={m.movie_id} value={m.movie_id}>
                        {m.movie_title}
                      </option>
                    ))}
                  </select>
                  {formErrors.movie_id && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.movie_id}
                    </p>
                  )}
                </div>

                {/* Showroom Select */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Showroom *
                  </label>
                  <select
                    name="showroom_id"
                    value={formData.showroom_id}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600"
                  >
                    <option value="">Select a Showroom</option>
                    {showrooms.map((s) => (
                      <option key={s.showroom_id} value={s.showroom_id}>
                        {s.showroom_name}
                      </option>
                    ))}
                  </select>
                  {formErrors.showroom_id && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.showroom_id}
                    </p>
                  )}
                </div>

                {/* Start Time */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Start Time *
                  </label>
                  <input
                    type="datetime-local"
                    name="start_time"
                    value={formData.start_time}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600"
                  />
                  {formErrors.start_time && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.start_time}
                    </p>
                  )}
                </div>

                {/* End Time */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    End Time{" "}
                    <span className="text-gray-500 text-xs">
                      (Optional - Defaults to +2.5h)
                    </span>
                  </label>
                  <input
                    type="datetime-local"
                    name="end_time"
                    value={formData.end_time}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-red-500 border border-gray-600"
                  />
                  {formErrors.end_time && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.end_time}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-4 pt-4">
                  <button
                    onClick={handleCloseModal}
                    className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={!!formErrors.conflict || isCheckingConflict}
                    className={`flex-1 px-6 py-3 text-white rounded-lg transition-colors ${
                      formErrors.conflict || isCheckingConflict
                        ? "bg-red-500/50 cursor-not-allowed"
                        : "bg-red-500 hover:bg-red-600"
                    }`}
                  >
                    {isCheckingConflict
                      ? "Checking..."
                      : modalMode === "add"
                      ? "Schedule"
                      : "Update"}
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

export default ManageShowtimesPage;
