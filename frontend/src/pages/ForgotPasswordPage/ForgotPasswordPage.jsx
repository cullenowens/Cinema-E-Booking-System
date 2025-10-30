import React, { useState } from "react";
import { resetPassword } from "../../api";
import { useNavigate } from "react-router-dom";

const ForgotPasswordPage = () => {
  const [verificationCode, setVerificationCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [email, setEmail] = useState("");

  const navigate = useNavigate();
  const handleSubmit = async () => {
    try {
      if (!verificationCode || !newPassword) {
        alert("Please enter both the verification code and new password.");
        return;
      }

      const response = await resetPassword(
        verificationCode,
        newPassword,
        email
      );

      navigate("/signin");
    } catch (error) {
      console.error(error);
      console.log(error.response?.data);
      alert("Failed to reset password.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-xl">
        <div className="bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700 flex flex-col items-center">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              Thank you for choosing eCinema.
            </h1>
            <p className="text-gray-400">
              Please enter your verification token, email, and new password
              below:
            </p>
          </div>
          <input
            type="text"
            placeholder="Verification Code"
            className="text-center text-white border border-gray-600 w-80 rounded-2xl mb-4 bg-transparent"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
          />
          <input
            type="text"
            placeholder="Email"
            className="text-center text-white border border-gray-600 w-80 rounded-2xl mb-4 bg-transparent"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="New Password"
            className="text-center text-white border border-gray-600 w-80 rounded-2xl bg-transparent"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <button
            className="mt-6 cursor-pointer bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors"
            onClick={handleSubmit}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
