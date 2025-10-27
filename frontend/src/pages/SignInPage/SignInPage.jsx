import React, { useState } from "react";
import PersonIcon from "@mui/icons-material/Person";
import LockIcon from "@mui/icons-material/Lock";
import EmailIcon from "@mui/icons-material/Email";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const SignInPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState({ type: "", text: "" });
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const navigate = useNavigate();

  const validateForm = () => {
    const newErrors = {};

    if (!username) {
      newErrors.username = "Username is required";
    } else if (username.length < 3) {
      newErrors.username = "Username must be at least 3 characters";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: "", text: "" });

    if (!validateForm()) return;

    const result = await login(username, password);
    navigate("/");
    if (!result.success) {
      setMessage({
        type: "error",
        text: result.error || "Invalid username or password",
      });
    }
  };

  const handleForgotPassword = (e) => {
    e.preventDefault();

    if (!forgotEmail) {
      setMessage({ type: "error", text: "Please enter your email address" });
      return;
    }

    if (!/\S+@\S+\.\S+/.test(forgotEmail)) {
      setMessage({ type: "error", text: "Please enter a valid email address" });
      return;
    }

    console.log("Password reset requested for:", forgotEmail);
    setMessage({
      type: "success",
      text: "Password reset link has been sent to your email.",
    });

    setTimeout(() => {
      setShowForgotPassword(false);
      setForgotEmail("");
      setMessage({ type: "", text: "" });
    }, 4000);
  };

  // --- Forgot Password View ---
  if (showForgotPassword) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              Reset Password
            </h1>
            <p className="text-gray-400">
              Enter your email to receive a password reset link
            </p>
          </div>

          {message.text && (
            <div
              className={`mb-6 p-4 rounded-lg ${
                message.type === "success"
                  ? "bg-green-900/30 border border-green-700"
                  : "bg-red-900/30 border border-red-700"
              }`}
            >
              <p
                className={`text-sm ${
                  message.type === "success" ? "text-green-300" : "text-red-300"
                }`}
              >
                {message.text}
              </p>
            </div>
          )}

          <div className="space-y-6">
            <div>
              <label
                htmlFor="forgotEmail"
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                Email Address <span className="text-red-400">*</span>
              </label>
              <div className="relative">
                <EmailIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
                <input
                  type="email"
                  id="forgotEmail"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <button
              onClick={handleForgotPassword}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition duration-200"
            >
              Send Reset Link
            </button>

            <button
              onClick={() => {
                setShowForgotPassword(false);
                setMessage({ type: "", text: "" });
              }}
              className="w-full text-gray-400 hover:text-white font-medium transition"
            >
              Back to Sign In
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- Sign In View ---
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-400">
            Sign in to your Cinema E-Booking account
          </p>
        </div>

        {message.text && (
          <div
            className={`mb-6 p-4 rounded-lg ${
              message.type === "success"
                ? "bg-green-900/30 border border-green-700"
                : "bg-red-900/30 border border-red-700"
            }`}
          >
            <p
              className={`text-sm ${
                message.type === "success" ? "text-green-300" : "text-red-300"
              }`}
            >
              {message.text}
            </p>
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Username <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <PersonIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={`w-full pl-10 pr-4 py-3 bg-gray-700 border ${
                  errors.username ? "border-red-500" : "border-gray-600"
                } rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                placeholder="Enter your username"
              />
            </div>
            {errors.username && (
              <p className="mt-2 text-sm text-red-400">{errors.username}</p>
            )}
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Password <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <LockIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`w-full pl-10 pr-12 py-3 bg-gray-700 border ${
                  errors.password ? "border-red-500" : "border-gray-600"
                } rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                placeholder="Enter your password"
              />
            </div>
            {errors.password && (
              <p className="mt-2 text-sm text-red-400">{errors.password}</p>
            )}
          </div>

          <div className="flex items-center justify-center">
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="text-sm text-blue-400 hover:text-blue-300 transition font-medium"
            >
              Forgot Password?
            </button>
          </div>

          <button
            onClick={handleSubmit}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition duration-200 shadow-lg"
          >
            Sign In
          </button>
        </div>

        <div className="mt-6 text-center">
          <p className="text-gray-400">
            Don't have an account?{" "}
            <a
              href="/register"
              className="text-blue-400 hover:text-blue-300 transition font-medium"
            >
              Sign Up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignInPage;
