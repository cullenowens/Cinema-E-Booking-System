import React, { useEffect, useState } from "react";
import Navbar from "../../components/Navbar/Navbar";
import { useSearchParams, useNavigate } from "react-router-dom";
import { searchMovies } from "../../api";
import Grid from "@mui/material/Grid";

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const [movies, setMovies] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState("");

  const navigate = useNavigate();

  const searchQuery = searchParams.get("q") || "";

  useEffect(() => {
    const fetchMovies = async () => {
      const data = await searchMovies(searchParams.get("q"));
      setMovies(data.movies || []);
      console.log(movies);
    };
    fetchMovies();
  }, [searchQuery]);

  const filteredMovies = selectedGenre
    ? movies.filter((movie) => movie.genres.includes(selectedGenre))
    : movies;

  return (
    <div className="bg-gray-800 min-h-300">
      <Navbar />{" "}
      <div className=" ml-20 mt-6">
        <select
          className="bg-gray-700 text-white px-3 py-2 rounded-lg"
          value={selectedGenre}
          onChange={(e) => setSelectedGenre(e.target.value)}
        >
          <option value="">All Genres</option>
          <option value="Action">Action</option>
          <option value="Comedy">Comedy</option>
          <option value="Drama">Drama</option>
          <option value="Horror">Horror</option>
          <option value="Music">Music</option>
          <option value="Sports">Sports</option>
          <option value="Animated">Animated</option>
          <option value="Fantasy">Fantasy</option>
          <option value="Thriller">Thriller</option>
          <option value="Crime">Crime</option>
          <option value="Adventure">Adventure</option>
          <option value="Sci-fi">Sci-fi</option>
          <option value="Mystery">Mystery</option>
          <option value="Concert">Concert</option>
        </select>
        <p className="text-white text-lg mt-3">
          {filteredMovies.length} search results for{" "}
          <span className="font-semibold text-red-300">"{searchQuery}"</span>
        </p>
      </div>
      <div></div>
      <div className="flex gap-20 grid mb-20 grid-cols-4 mx-20 mt-10 ">
        {filteredMovies.map((movie, index) => (
          <img
            src={movie.poster_url}
            key={index}
            className="h-115 w-82 cursor-pointer m-auto"
            onClick={() => {
              navigate(`/movie/${movie.movie_id}`);
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default SearchPage;
