import React from "react";
import Navbar from "../../components/Navbar/Navbar";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Scrollbar, A11y } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/scrollbar";

const HomePage = () => {
  return (
    <div className="bg-gray-600 h-screen">
      <Navbar />
      <img src="/Apple_TV_F1_key_art_graphic_header_4_1_show_home.jpg.large_2x.jpg" />

      <div className="text-white text-center flex justify-between mt-10 max-w-6xl items-center mx-auto mb-3">
        <div className="text-4xl">Movies at eCinema</div>
        <div className="flex gap-5 text-xl">
          <button>Now Showing</button>
          <button>Coming Soon</button>
        </div>
      </div>
      <hr className="text-white max-w-7xl mx-auto mb-15" />
      <Swiper
        modules={[Navigation]}
        spaceBetween={50}
        slidesPerView={3}
        navigation
        onSlideChange={() => console.log("slide change")}
        onSwiper={(swiper) => console.log(swiper)}
        className="text-center max-w-5xl h-20"
      >
        <SwiperSlide>Movie 1</SwiperSlide>
        <SwiperSlide>Movie 2</SwiperSlide>
        <SwiperSlide>Movie 3</SwiperSlide>
        <SwiperSlide>Movie 4</SwiperSlide>
      </Swiper>
    </div>
  );
};

export default HomePage;
