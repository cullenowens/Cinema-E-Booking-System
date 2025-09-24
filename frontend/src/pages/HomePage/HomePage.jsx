import React from "react";
import Navbar from "../../components/Navbar/Navbar";

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
      <hr className="text-white max-w-7xl mx-auto" />
    </div>
  );
};

export default HomePage;
