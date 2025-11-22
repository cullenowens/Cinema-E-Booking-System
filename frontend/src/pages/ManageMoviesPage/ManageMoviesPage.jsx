import React, { useState, useEffect } from "react";
import {
  getAllMovies,
  createMovie,
  updateMovie,
  deleteMovie,
  getGenres,
} from "../../api";
import Navbar from "../../components/Navbar/Navbar";

const ManageMovies = () => {
  const [movies, setMovies] = useState([]);
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState("add");
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [formData, setFormData] = useState({
    movie_title: "",
    movie_description: "",
    age_rating: "PG",
    poster_url: "",
    trailer_url: "",
    movie_status: "Coming Soon",
    genres: [],
  });
  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    fetchMovies();
    fetchGenres();
  }, []);

  const fetchMovies = async () => {
    try {
      setLoading(true);
      const data = await getAllMovies();
      setMovies(data.movies || []);
    } catch (error) {
      console.error("Error fetching movies:", error);
      alert("Failed to load movies. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchGenres = async () => {
    try {
      const data = await getGenres();
      setGenres(data.genres || []);
    } catch (error) {
      console.error("Error fetching genres:", error);
      alert("Failed to load genres. Please try again.");
    }
  };

  const handleOpenModal = (mode, movie = null) => {
    setModalMode(mode);
    setFormErrors({});

    if (mode === "edit" && movie) {
      setSelectedMovie(movie);
      setFormData({
        movie_title: movie.movie_title,
        movie_description: movie.movie_description,
        age_rating: movie.age_rating,
        poster_url: movie.poster_url,
        trailer_url: movie.trailer_url,
        movie_status: movie.movie_status,
        genres: movie.genres || [],
      });
    } else {
      setSelectedMovie(null);
      setFormData({
        movie_title: "",
        movie_description: "",
        age_rating: "PG",
        poster_url: "",
        trailer_url: "",
        movie_status: "Coming Soon",
        genres: [],
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedMovie(null);
    setFormErrors({});
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleGenreToggle = (genreName) => {
    setFormData((prev) => ({
      ...prev,
      genres: prev.genres.includes(genreName)
        ? prev.genres.filter((g) => g !== genreName)
        : [...prev.genres, genreName],
    }));
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.movie_title.trim()) {
      errors.movie_title = "Movie title is required";
    }

    if (!formData.movie_description.trim()) {
      errors.movie_description = "Description is required";
    } else if (formData.movie_description.trim().length < 10) {
      errors.movie_description = "Description must be at least 10 characters";
    }

    if (!formData.poster_url.trim()) {
      errors.poster_url = "Poster URL is required";
    } else if (
      !formData.poster_url.startsWith("http://") &&
      !formData.poster_url.startsWith("https://")
    ) {
      errors.poster_url = "Poster URL must start with http:// or https://";
    }

    if (!formData.trailer_url.trim()) {
      errors.trailer_url = "Trailer URL is required";
    } else if (
      !formData.trailer_url.startsWith("http://") &&
      !formData.trailer_url.startsWith("https://")
    ) {
      errors.trailer_url = "Trailer URL must start with http:// or https://";
    }

    if (formData.genres.length === 0) {
      errors.genres = "Please select at least one genre";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      if (modalMode === "add") {
        await createMovie(formData);
        alert("Movie added successfully!");
      } else {
        await updateMovie(selectedMovie.movie_id, formData);
        alert("Movie updated successfully!");
      }
      handleCloseModal();
      fetchMovies(); // Refresh the movie list
    } catch (error) {
      console.error("Error saving movie:", error);
      if (error.response?.data?.details) {
        setFormErrors(error.response.data.details);
      } else {
        alert(
          error.response?.data?.error ||
            `Failed to ${modalMode === "add" ? "add" : "update"} movie`
        );
      }
    }
  };

  const handleDelete = async (movieId, movieTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${movieTitle}"?`)) {
      return;
    }

    try {
      await deleteMovie(movieId);
      alert("Movie deleted successfully!");
      fetchMovies(); // Refresh the movie list
    } catch (error) {
      console.error("Error deleting movie:", error);
      alert(error.response?.data?.error || "Failed to delete movie");
    }
  };

  const filteredMovies = movies.filter((movie) =>
    movie.movie_title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-red-300">Manage Movies</h1>
            <button
              onClick={() => handleOpenModal("add")}
              className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <span className="text-xl">+</span>
              Add New Movie
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
              placeholder="Search movies by title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-gray-800 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Total Movies</p>
              <p className="text-2xl font-bold">{movies.length}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Currently Running</p>
              <p className="text-2xl font-bold">
                {
                  movies.filter((m) => m.movie_status === "Currently Running")
                    .length
                }
              </p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Coming Soon</p>
              <p className="text-2xl font-bold">
                {movies.filter((m) => m.movie_status === "Coming Soon").length}
              </p>
            </div>
          </div>

          {/* Movies Grid */}
          {filteredMovies.length === 0 ? (
            <div className="text-center py-12 bg-gray-800 rounded-lg">
              <p className="text-gray-400 text-lg">No movies found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredMovies.map((movie) => (
                <div
                  key={movie.movie_id}
                  className="bg-gray-800 rounded-lg overflow-hidden hover:shadow-xl transition-shadow"
                >
                  <img
                    src={movie.poster_url}
                    alt={movie.movie_title}
                    className="w-full h-64 object-cover"
                    onError={(e) => {
                      e.target.src =
                        "https://via.placeholder.com/300x450?text=No+Image";
                    }}
                  />
                  <div className="p-4">
                    <h3 className="text-xl font-bold mb-2">
                      {movie.movie_title}
                    </h3>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 bg-gray-700 rounded text-xs">
                        {movie.age_rating}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          movie.movie_status === "Currently Running"
                            ? "bg-green-600"
                            : "bg-yellow-600"
                        }`}
                      >
                        {movie.movie_status}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                      {movie.movie_description}
                    </p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {movie.genres?.map((genre, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-red-900 text-red-200 rounded text-xs"
                        >
                          {genre}
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleOpenModal("edit", movie)}
                        className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() =>
                          handleDelete(movie.movie_id, movie.movie_title)
                        }
                        className="flex-1 flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-gray-800 rounded-lg w-full max-w-2xl my-8">
              {/* Modal Header */}
              <div className="flex justify-between items-center p-6 border-b border-gray-700">
                <h2 className="text-2xl font-bold">
                  {modalMode === "add" ? "Add New Movie" : "Edit Movie"}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="text-gray-400 hover:text-white transition-colors text-2xl"
                >
                  ✕
                </button>
              </div>

              {/* Modal Body */}
              <div className="p-6 space-y-4">
                {/* Movie Title */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Movie Title *
                  </label>
                  <input
                    type="text"
                    name="movie_title"
                    value={formData.movie_title}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Enter movie title"
                  />
                  {formErrors.movie_title && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.movie_title}
                    </p>
                  )}
                </div>

                {/* Movie Description */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Description *
                  </label>
                  <textarea
                    name="movie_description"
                    value={formData.movie_description}
                    onChange={handleInputChange}
                    rows="4"
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Enter movie description"
                  />
                  {formErrors.movie_description && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.movie_description}
                    </p>
                  )}
                </div>

                {/* Age Rating and Status */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Age Rating *
                    </label>
                    <select
                      name="age_rating"
                      value={formData.age_rating}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      <option value="G">G</option>
                      <option value="PG">PG</option>
                      <option value="PG-13">PG-13</option>
                      <option value="R">R</option>
                      <option value="NC-17">NC-17</option>
                      <option value="NR">NR</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Status *
                    </label>
                    <select
                      name="movie_status"
                      value={formData.movie_status}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      <option value="Coming Soon">Coming Soon</option>
                      <option value="Currently Running">
                        Currently Running
                      </option>
                    </select>
                  </div>
                </div>

                {/* Poster URL */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Poster URL *
                  </label>
                  <input
                    type="url"
                    name="poster_url"
                    value={formData.poster_url}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="https://example.com/poster.jpg"
                  />
                  {formErrors.poster_url && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.poster_url}
                    </p>
                  )}
                </div>

                {/* Trailer URL */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Trailer URL *
                  </label>
                  <input
                    type="url"
                    name="trailer_url"
                    value={formData.trailer_url}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="https://youtube.com/watch?v=..."
                  />
                  {formErrors.trailer_url && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.trailer_url}
                    </p>
                  )}
                </div>

                {/* Genres */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Genres * (Select at least one)
                  </label>
                  <div className="grid grid-cols-3 gap-2 max-h-40 overflow-y-auto p-2 bg-gray-700 rounded-lg">
                    {genres.map((genre) => (
                      <label
                        key={genre.genre_id}
                        className="flex items-center space-x-2 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={formData.genres.includes(genre.genre_name)}
                          onChange={() => handleGenreToggle(genre.genre_name)}
                          className="w-4 h-4 text-red-500 bg-gray-600 border-gray-500 rounded focus:ring-red-500"
                        />
                        <span className="text-sm">{genre.genre_name}</span>
                      </label>
                    ))}
                  </div>
                  {formErrors.genres && (
                    <p className="text-red-400 text-sm mt-1">
                      {formErrors.genres}
                    </p>
                  )}
                </div>

                {/* Form Actions */}
                <div className="flex gap-4 pt-4">
                  <button
                    onClick={handleCloseModal}
                    className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit}
                    className="flex-1 px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                  >
                    {modalMode === "add" ? "Add Movie" : "Update Movie"}
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

export default ManageMovies;
