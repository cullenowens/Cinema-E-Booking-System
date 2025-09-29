import React, { useEffect, useState } from "react";
import Navbar from "../../components/Navbar/Navbar";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/scrollbar";
import { getCurrentMovies, getFutureMovies } from "../../api";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const navigate = useNavigate();

  const [currentMovies, setCurrentMovies] = useState([]);
  const [futureMovies, setFutureMovies] = useState([]);

  const [isCurrent, setIsCurrent] = useState(true);

  useEffect(() => {
    const fetchMovies = async () => {
      const currData = await getCurrentMovies();
      const futData = await getFutureMovies();

      setCurrentMovies(currData || []);
      setFutureMovies(futData || []);
    };
    fetchMovies();
  }, []);

  const displayMovies = isCurrent ? currentMovies : futureMovies;
  const allMovies = [...currentMovies, ...futureMovies];

  return (
    <div className="bg-gray-800 h-450">
      <Navbar />
      <img src="/Apple_TV_F1_key_art_graphic_header_4_1_show_home.jpg.large_2x.jpg" />

      <div className="text-white text-center flex justify-between mt-10 max-w-6xl items-center mx-auto mb-3">
        <div className="text-4xl">Movies at eCinema</div>
        <div className="flex gap-5 text-xl">
          <button
            className={`cursor-pointer hover:bg-black transition-all duration-100 px-1 ${
              isCurrent ? "border-b-2" : ""
            }`}
            onClick={() => setIsCurrent(true)}
          >
            Now Showing
          </button>
          <button
            className={`cursor-pointer hover:bg-black transition-all duration-100 px-1 ${
              !isCurrent ? "border-b-2" : ""
            }`}
            onClick={() => setIsCurrent(false)}
          >
            Coming Soon
          </button>
        </div>
      </div>
      <hr className="text-white max-w-7xl mx-auto mb-15" />
      <Swiper
        modules={[Navigation]}
        slidesPerView={3}
        navigation
        pagination={{ clickable: true }}
        className="text-center max-w-7xl mb-20"
      >
        {displayMovies.map((movie, index) => (
          <SwiperSlide key={index}>
            <img
              src={movie.poster_url}
              className="h-115 cursor-pointer mx-auto"
              onClick={() => {
                navigate(`/movie/${movie.movie_id}`);
              }}
            />
          </SwiperSlide>
        ))}
      </Swiper>
      <div className="text-white ml-95 mt-10 max-w-6xl  mb-3">
        <div className="text-4xl">Movie Trailers</div>
      </div>
      <hr className="text-white max-w-7xl mx-auto mb-15" />
      <Swiper
        modules={[Navigation]}
        slidesPerView={3}
        navigation
        pagination={{ clickable: true }}
        className="text-center mb-20 max-w-7xl"
      >
        {allMovies.map((movie, index) => (
          <SwiperSlide key={index}>
            <iframe src={movie.trailer_url} className="h-50 mx-auto" />
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};

export default HomePage;
