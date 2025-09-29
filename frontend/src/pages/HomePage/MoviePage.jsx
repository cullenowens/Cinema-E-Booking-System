import React, {useState, useEffect} from "react";
import { useParams } from "react-router-dom";
import { getMovieDetails } from "../../api/index";

const MoviePage = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [selectedShowtime, setSelectedShowtime] = useState(null);
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

  const handleShowtimeClick = (time) => {
    setSelectedShowtime(time);
    navigate('/booking/${id}?showtime=${time}');
  };

  if (!movie) return <div>Movie not found</div>;
  
  return (
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
          <div className="col-span-1 flex flex-col justify-between">
            <div className="space-y-4">
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
                <p className="text-base leading-relaxed">{movie.movie_description}</p>
              </div>
            </div>

            {/* Showtimes at bottom of middle column */}
            <div className="mt-auto">
              <p className="text-gray-400 text-sm mb-2">Showtimes</p>
              <div className="flex flex-wrap gap-2">
                {movie.showtimes?.map((time, index) => (
                  <button 
                    key={index}
                    onClick={() => handleShowtimeClick(time)}
                    className="bg-gray-700 px-3 py-1 rounded text-sm"
                  >
                    {time}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Trailer */}
          <div className="col-span-1">
            {movie.trailer_url && (
              <div className="h-full flex flex-col">
                <p className="text-gray-400 text-sm mb-3">Trailer</p>
                <iframe
                  className="w-full flex-1 rounded-lg"
                  src={movie.trailer_url}
                  title="Movie Trailer"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoviePage;
