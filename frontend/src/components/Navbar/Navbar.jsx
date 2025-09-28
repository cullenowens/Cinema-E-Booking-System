import React from "react";
import { useNavigate } from "react-router-dom";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";

const Navbar = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-gray-800 shadow-lg">
      <div className="h-16 mx-auto flex justify-between items-center px-12">
        <div className="flex items-center gap-35">
          <h1 className="text-red-300 text-3xl">eCinema</h1>
          <div className="flex gap-15">
            <button
              onClick={() => navigate("/")}
              className="text-white cursor-pointer hover:bg-gray-800 transition-colors p-1"
            >
              Home
            </button>
            <button
              onClick={() => navigate("/movies")}
              className="text-white cursor-pointer hover:bg-gray-800 transition-colors p-1"
            >
              Movies
            </button>
            <input
              type="text"
              placeholder="Search for movies..."
              className="text-gray-500 bg-white rounded-xl pl-2 w-70 pr-2 text-left focus:outline-none focus:ring-2 focus:ring-red-300 focus:border-transparent"
            />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <AccountCircleIcon sx={{ color: "white" }} />
          <button
            onClick={() => navigate("/signin")}
            className="text-white cursor-pointer hover:bg-gray-800 transition-colors p-1"
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
