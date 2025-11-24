import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import { useAuth } from "../../contexts/AuthContext";

const Navbar = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [searchInput, setSearchInput] = useState("");

  const { user } = useAuth();

  const isAdmin = user && user.is_staff;

  console.log(user);
  useEffect(() => {
    const q = searchParams.get("q") || "";
    setSearchInput(q);
  }, [searchParams]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const searchTerm = searchInput.trim();
    if (searchTerm) {
      navigate(`/search?q=${encodeURIComponent(searchTerm)}`);
    }
  };

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

            <form onSubmit={handleSearchSubmit}>
              <input
                type="text"
                placeholder="Search for movies..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="text-gray-500 bg-white rounded-xl pl-2 w-70 pr-2 text-left focus:outline-none focus:ring-2 focus:ring-red-300 focus:border-transparent"
              />
            </form>
            {/* Show Admin Portal button only if isAdmin is true */}
            {isAdmin && (
              <button
                onClick={() => navigate("/admin")}
                className="text-white cursor-pointer hover:bg-gray-800 transition-colors p-1"
              >
                Admin Portal
              </button>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <AccountCircleIcon sx={{ color: "white" }} />
          {user ? (
            <button
              onClick={() => navigate("/profile")}
              className="text-white cursor-pointer hover:bg-gray-800 transition-colors p-1"
            >
              {user.username}
            </button>
          ) : (
            <button
              onClick={() => navigate("/signin")}
              className="text-white cursor-pointer hover:bg-gray-800 transition-colors p-1"
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Navbar;
