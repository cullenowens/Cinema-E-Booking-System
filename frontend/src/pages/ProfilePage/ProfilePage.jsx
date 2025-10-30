import React, { useState, useEffect } from "react";
import { useAuth } from "../../contexts/AuthContext";
import Navbar from "../../components/Navbar/Navbar";
import { useNavigate } from "react-router-dom";
import { getAddress, updateAddress, updateProfile } from "../../api";

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    firstName: "",
    lastName: "",
    phone: "",
    address: "",
    city: "",
    state: "",
    zipCode: "",
    promotions: false,
  });

  const [showPasswordModal, setShowPasswordModal] = useState(false);

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  // Populate form when user data becomes available
  useEffect(() => {
    const fetchData = async () => {
      if (user) {
        try {
          const addressData = await getAddress();
          setFormData({
            username: user.username || "",
            firstName: user.first_name || "",
            lastName: user.last_name || "",
            phone: user.phone || "",
            address: addressData.street || "",
            city: addressData.city || "",
            state: addressData.state || "",
            zipCode: addressData.zip_code || "",
            promotions: user.subscribed || false,
          });
        } catch (error) {
          console.log(error.response?.data);
        }
      }
    };
    fetchData();
  }, [user]);

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await updateProfile({
        phone: formData.phone,
        subscribed: formData.promotions,
      });

      const addressRes = await updateAddress({
        street: formData.address,
        city: formData.city,
        state: formData.state,
        zip_code: formData.zipCode,
      });

      alert("Profile updated");
    } catch (err) {
      if (err.response.status === 404) {
        
        const { createAddress } = await import("../../api");
        await createAddress({
          street: formData.address,
          city: formData.city,
          state: formData.state,
          zip_code: formData.zipCode,
        });
        alert("Profile and address created!");
      } else {
        console.error("Error updating profile:", err);
        alert("Failed to update profile");
      }
        //await axios.post(`${url}/auth/address/`, addressData, {
        //  headers: { Authorization: `Bearer ${token}` },
        //});
    }
  };

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  const handlePasswordChange = (e) => {
    e.preventDefault();
    console.log("Password change:", passwordData);
    // TODO: send request to backend
    setShowPasswordModal(false);
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-6">
        <div className="w-full max-w-4xl">
          <h1 className="mb-6 text-white text-3xl font-semibold text-center">
            Profile Information
          </h1>

          <form
            onSubmit={handleSubmit}
            className="bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700 space-y-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-gray-300 mb-2">Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">First Name</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">Last Name</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">Phone Number</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">Home Address</label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">City</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">State</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">ZIP Code</label>
                <input
                  type="text"
                  name="zipCode"
                  value={formData.zipCode}
                  onChange={handleChange}
                  className="w-full p-3 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center mt-4">
              <input
                type="checkbox"
                name="promotions"
                checked={formData.promotions}
                onChange={handleChange}
                className="w-5 h-5 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
              />
              <label className="ml-3 text-gray-300">
                Register for promotions?
              </label>
            </div>

            <div className="flex flex-col md:flex-row justify-between items-center gap-4 mt-8">
              <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
                <button
                  type="button"
                  onClick={() => setShowPasswordModal(true)}
                  className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-6 rounded-xl transition-all duration-200"
                >
                  Change Password
                </button>

                <button
                  type="button"
                  onClick={() => navigate("/payment-methods")}
                  className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-6 rounded-xl transition-all duration-200"
                >
                  Add Credit Card
                </button>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
                <button
                  type="button"
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  Log Out
                </button>

                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {showPasswordModal && (
        <div className="fixed inset-0 backdrop-filter backdrop-blur-lg bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-8 rounded-2xl w-full max-w-md shadow-xl border border-gray-700">
            <h2 className="text-2xl text-white font-semibold mb-6 text-center">
              Change Password
            </h2>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <input
                type="password"
                name="currentPassword"
                placeholder="Current Password"
                value={passwordData.currentPassword}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    currentPassword: e.target.value,
                  })
                }
                className="w-full p-3 rounded-lg bg-gray-700 text-white focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="password"
                name="newPassword"
                placeholder="New Password"
                value={passwordData.newPassword}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    newPassword: e.target.value,
                  })
                }
                className="w-full p-3 rounded-lg bg-gray-700 text-white focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="password"
                name="confirmPassword"
                placeholder="Confirm New Password"
                value={passwordData.confirmPassword}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    confirmPassword: e.target.value,
                  })
                }
                className="w-full p-3 rounded-lg bg-gray-700 text-white focus:ring-2 focus:ring-blue-500"
              />

              <div className="flex justify-between mt-6">
                <button
                  type="button"
                  onClick={() => setShowPasswordModal(false)}
                  className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg"
                >
                  Update Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default ProfilePage;
