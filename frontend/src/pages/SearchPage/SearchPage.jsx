import React, { useEffect, useState } from "react";
import Navbar from "../../components/Navbar/Navbar";
import { useSearchParams, useNavigate } from "react-router-dom";
import { searchMovies } from "../../api";
import Grid from "@mui/material/Grid";

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const [movies, setMovies] = useState([]);

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

  return (
    <div className="bg-gray-800 min-h-300">
      <Navbar />{" "}
      <div className="flex gap-20 grid mb-20 grid-cols-4 mx-20 mt-10 ">
        {movies.map((movie, index) => (
          <img
            src={movie.poster_url}
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
