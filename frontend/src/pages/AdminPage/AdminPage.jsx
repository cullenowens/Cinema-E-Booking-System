import React from "react";
import Navbar from "../../components/Navbar/Navbar";
import { useNavigate } from "react-router-dom";

const AdminPage = () => {
  const navigate = useNavigate();

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex justify-center p-4">
        <div className="w-full max-w-md">
          <h1 className="text-4xl text-white text-center font-bold mb-6 mt-7">
            Admin Portal
          </h1>
          <div
            className="cursor-pointer hover:border-cyan-600 hover:scale-105 transition-all duration-200 bg-gray-800 mb-6 rounded-2xl shadow-2xl p-8 border border-gray-700 text-3xl text-white text-center font-medium tracking-wide"
            onClick={() => navigate("/admin/manage-movies")}
          >
            Manage Movies
          </div>
          <div
            className="cursor-pointer hover:border-cyan-600 hover:scale-105 transition-all duration-200 bg-gray-800 mb-6 rounded-2xl shadow-2xl p-8 border border-gray-700 text-3xl text-white text-center font-medium tracking-wide"
            onClick={() => navigate("/admin/manage-showtimes")}
          >
            Manage Showtimes
          </div>
          <div
            className="cursor-pointer hover:border-cyan-600 hover:scale-105 transition-all duration-200 bg-gray-800 mb-6 rounded-2xl shadow-2xl p-8 border border-gray-700 text-3xl text-white text-center font-medium tracking-wide"
            onClick={() => navigate("/admin/manage-promotions")}
          >
            Manage Promotions
          </div>

          <div
            className="cursor-pointer hover:border-cyan-600 hover:scale-105 transition-all duration-200 bg-gray-800 mb-6 rounded-2xl shadow-2xl p-8 border border-gray-700 text-3xl text-white text-center font-medium tracking-wide"
            onClick={() => navigate("/admin/manage-users")}
          >
            Manage Users
          </div>
        </div>
      </div>
    </>
  );
};

export default AdminPage;
