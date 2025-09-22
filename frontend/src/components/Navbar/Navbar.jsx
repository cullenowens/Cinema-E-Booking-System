import React from "react";
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-[#003366] shadow-lg">
      <div className="mx-auto max-w-7xl px-4">
        <div className="h-20 flex justify-between items-center">
          <img
            src="/interface-icon-assets-icon-camera-icon-technology-icon-photo-camera-icon-photograph-icon-text-circle-line-cameras-optics-symbol-png-clipart.jpg"
            className="h-15"
          />
          <button
            onClick={() => navigate("/showtimes")}
            className="text-white cursor-pointer"
          >
            SHOWTIMES
          </button>
          <button
            onClick={() => navigate("/promotions")}
            className="text-white cursor-pointer"
          >
            PROMOTIONS
          </button>
          <button
            onClick={() => navigate("/contact")}
            className="text-white cursor-pointer"
          >
            CONTACT
          </button>
          <button
            onClick={() => navigate("/login")}
            className="text-white cursor-pointer"
          >
            LOGIN
          </button>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
