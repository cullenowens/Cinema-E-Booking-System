import React from "react";
import Navbar from "../../components/Navbar/Navbar";

const ManageUsersPage = () => {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-red-300">Manage Users</h1>
            {/* Placeholder for Add User button or other actions */}
          </div>

          {/* Placeholder for User List/Table */}
          <div className="bg-gray-800 rounded-lg shadow-xl border border-gray-700 p-8 text-center">
            <p className="text-gray-400 text-lg">
              User management functionality coming soon.
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default ManageUsersPage;
