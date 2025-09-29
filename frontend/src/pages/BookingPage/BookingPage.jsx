import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";
import { getMovieDetails } from "../../api";

const BookingPage = () => {
  const { id, showtime } = useParams();
  const [movie, setMovie] = useState(null);
  const time = decodeURIComponent(showtime);

  useEffect(() => {
    const fetchMovie = async () => {
      try {
        const movieData = await getMovieDetails(id);
        setMovie(movieData);
      } catch (error) {
        console.error("Error fetching movie details:", error);
      }
    };

    if (id) {
      fetchMovie();
    }
  }, [id]);

  if (!movie) {
    return (
      <div>
        <Navbar />
        <div className="bg-gray-900 min-h-screen text-white p-8"></div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <div className="bg-gray-900 min-h-screen text-white p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">
            Book seats for {movie.movie_title}{" "}
          </h1>
          <p className="text-gray-400 mb-8">Showtime: {showtime}</p>
          <div className="bg-gray-800 rounded-lg p-6 text-center\">
            <p className="text-gray-300">
              Seat selection and checkout coming soon
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingPage;
