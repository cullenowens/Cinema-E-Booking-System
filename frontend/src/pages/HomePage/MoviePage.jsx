import React from "react";
import { useParams } from "react-router-dom";
import { getMovieDetails } from "../../api/index";

const MoviePage = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
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

  if (!movie) return <div>Movie not found</div>;
  
  return (
    <div className="bg-gray-800 h-450">
      <h1> {movie.movie_title}</h1>
      <div className="text-white text-center flex justify-between mt-10 max-w-6xl items-center mx-auto mb-3">
          <img src={movie.poster_url} alt={movie.movie_title} />
          <div className="flex gap-5 text-xl">
             <p><strong>Description:</strong> {movie.movie_description}</p>
             <p><strong>Rating:</strong> {movie.age_rating}</p>
            <p><strong>Status:</strong> {movie.movie_status}</p>
            <p><strong>Genres:</strong> {movie.genres?.join(", ")}</p>
            <div className="flex gap-5 text-xl">
              <strong>Showtimes:</strong>
              <ul>
                {movie.showtimes?.map((time, index) => (
                  <li key={index}>{time}</li>
                ))}
             </ul>
            </div>
          </div>
      </div>
      {movie.trailer_url && (
        <div className="mt-5 text-center">
          <a> Watch Trailer: </a>
          <iframe
            width="560"
            height="315"
            src={movie.trailer_url}
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
      )}
    </div>
  );
};

export default MoviePage;
