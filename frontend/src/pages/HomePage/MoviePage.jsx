import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getMovieDetails, getUserMovieShowings } from "../../api/index";
import Navbar from "../../components/Navbar/Navbar";

const MoviePage = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [showings, setShowings] = useState([]);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch basic movie details (title, desc, etc.)
        const movieData = await getMovieDetails(id);
        setMovie(movieData);

        // Fetch actual scheduled showings (dates, times, showrooms)
        // We use the user-facing endpoint that returns specific showing instances
        const showingsResponse = await getUserMovieShowings(id);

        setShowings(showingsResponse.showings || []);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id]);

  const handleShowtimeClick = (showing) => {
    // Navigate to booking page.
    // Currently using start_time string as the 'showtime' parameter to match existing routing.
    // In a full implementation, this would ideally pass showing.showing_id.
    const formattedTime = new Date(showing.start_time).toLocaleString();
    navigate(`/booking/${id}/${encodeURIComponent(formattedTime)}`);
  };

  // Helper to group showings by date (e.g., "Fri, Nov 15")
  const groupedShowings = showings.reduce((groups, showing) => {
    const dateObj = new Date(showing.start_time);
    const dateStr = dateObj.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });

    if (!groups[dateStr]) {
      groups[dateStr] = [];
    }
    groups[dateStr].push(showing);
    return groups;
  }, {});

  if (!movie)
    return (
      <div>
        <Navbar />
        <div className="bg-gray-900 min-h-screen text-white p-8"></div>
      </div>
    );

  return (
    <>
      <Navbar />
      <div className="bg-gray-900 min-h-screen text-white p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <h1 className="text-4xl font-bold mb-6">{movie.movie_title}</h1>

          {/* Main Content Grid */}
          <div className="grid grid-cols-3 gap-8 h-[calc(100vh-200px)]">
            {/* Left: Poster */}
            <div className="col-span-1">
              <img
                src={movie.poster_url}
                alt={movie.movie_title}
                className="w-full h-full object-cover rounded-lg shadow-lg"
              />
            </div>

            {/* Middle: Details */}
            <div className="col-span-1 flex flex-col justify-between h-full">
              <div className="space-y-4 overflow-y-auto">
                <div>
                  <p className="text-gray-400 text-sm">Rating</p>
                  <p className="text-xl font-semibold">{movie.age_rating}</p>
                </div>

                <div>
                  <p className="text-gray-400 text-sm">Status</p>
                  <p className="text-xl font-semibold">{movie.movie_status}</p>
                </div>

                <div>
                  <p className="text-gray-400 text-sm">Genres</p>
                  <p className="text-xl">{movie.genres?.join(", ")}</p>
                </div>

                <div>
                  <p className="text-gray-400 text-sm mb-2">Description</p>
                  <p className="text-base leading-relaxed">
                    {movie.movie_description}
                  </p>
                </div>
              </div>

              {/* Showtimes Section */}
              <div className="mt-6 pt-4 border-t border-gray-800 overflow-y-auto max-h-[40%]">
                <p className="text-gray-400 text-sm mb-3 font-bold uppercase tracking-wider">
                  Select a Showtime
                </p>

                {Object.keys(groupedShowings).length > 0 ? (
                  <div className="space-y-4">
                    {Object.entries(groupedShowings).map(
                      ([date, dailyShowings]) => (
                        <div key={date}>
                          <p className="text-red-300 text-xs font-medium mb-2">
                            {date}
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {dailyShowings.map((showing) => (
                              <button
                                key={showing.showing_id}
                                onClick={() => handleShowtimeClick(showing)}
                                className="bg-gray-800 border border-gray-600 px-3 py-2 rounded text-sm hover:bg-blue-600 hover:border-blue-500 transition-all cursor-pointer text-white shadow-sm"
                                title={`Showroom: ${showing.showroom_name}`}
                              >
                                {new Date(
                                  showing.start_time
                                ).toLocaleTimeString("en-US", {
                                  hour: "numeric",
                                  minute: "2-digit",
                                })}
                              </button>
                            ))}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-gray-500 italic">
                    No scheduled showtimes found.
                  </p>
                )}
              </div>
            </div>

            {/* Right: Trailer */}
            <div className="col-span-1">
              {movie.trailer_url && (
                <div className="h-full flex flex-col">
                  <p className="text-gray-400 text-sm mb-3">Trailer</p>
                  <iframe
                    className="w-full flex-1 rounded-lg shadow-lg bg-black"
                    src={movie.trailer_url}
                    title="Movie Trailer"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default MoviePage;
