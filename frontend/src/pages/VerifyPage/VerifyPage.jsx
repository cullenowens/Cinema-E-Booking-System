import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { verifyUser } from "../../api";

const VerifyPage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [verificationCode, setVerificationCode] = useState("");

  const searchParams = new URLSearchParams(location.search);
  const email = searchParams.get("email");

  const handleSubmit = async () => {
    try {
      verifyUser(email, verificationCode);
      console.log(verificationCode);
      navigate("/signin");
    } catch (error) {
      console.error("Error verifying code:", error);
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
              Please enter your verification code below:
            </p>
          </div>
          <input
            type="text"
            className="text-center text-2xl font-bold text-white border border-gray-600 w-40 rounded-2xl"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
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

export default VerifyPage;
