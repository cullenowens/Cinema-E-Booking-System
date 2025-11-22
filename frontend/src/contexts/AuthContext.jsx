import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/api/auth";

// Create context
const AuthContext = createContext();

// Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (username, password) => {
    try {
      const res = await axios.post(
        `${API_URL}/login/`,
        { username, password },
        { withCredentials: false }
      );

      // Store JWT tokens
      localStorage.setItem("accessToken", res.data.access);
      localStorage.setItem("refreshToken", res.data.refresh);

      axios.defaults.headers.common[
        "Authorization"
      ] = `Bearer ${res.data.access}`;

      // Set user
      setUser(res.data.user);
      console.log("Logged in user:", res.data.user);

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || "Login failed",
      };
    }
  };

  const register = async (username, email, password, phone, subscribed) => {
    try {
      const res = await axios.post(`${API_URL}/register/`, {
        username,
        email,
        password,
        phone_number: phone,
        subscribed,
      });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: JSON.stringify(error.response?.data) || "Registration failed",
      };
    }
  };

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const res = await axios.get(`${API_URL}/profile/`);
      setUser(res.data);
    } catch (error) {
      setUser(null);
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      delete axios.defaults.headers.common["Authorization"];
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await axios.post(
        `${API_URL}/logout/`,
        { refresh: refreshToken },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
        }
      );
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      delete axios.defaults.headers.common["Authorization"];
      navigate("/");
    }
  };

  // Run on mount
  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        register,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Hook for consuming auth context
export const useAuth = () => useContext(AuthContext);
