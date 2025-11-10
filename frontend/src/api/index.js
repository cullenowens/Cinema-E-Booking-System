import axios from "axios";

const url = "http://127.0.0.1:8000/api";

export const getCurrentMovies = async () => {
  const res = await axios.get(`${url}/movies/currently_running`);
  return res.data;
};

export const getFutureMovies = async () => {
  const res = await axios.get(`${url}/movies/coming-soon`);
  return res.data;
};

export const searchMovies = async (query) => {
  const res = await axios.get(`${url}/movies/search/?q=${query}`);
  return res.data;
};
export const getMovieDetails = async (id) => {
  const res = await axios.get(`${url}/movies/${id}`);
  return res.data;
};

export const verifyUser = async (email, verificationCode) => {
  const res = await axios.post(`${url}/auth/verify/`, {
    email: email,
    verification_code: verificationCode,
  });
  return res.data;
};

export const getAddress = async () => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.get(`${url}/auth/address/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const updateAddress = async (addressData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.put(`${url}/auth/address/`, addressData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const getPaymentCards = async () => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.get(`${url}/auth/payment-cards/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const addPaymentCard = async (cardData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.post(`${url}/auth/payment-cards/`, cardData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const updatePaymentCard = async (cardId, cardData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.put(`${url}auth/payment-cards/${cardId}/`, cardData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const deletePaymentCard = async (cardId) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.delete(`${url}/auth/payment-cards/${cardId}/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const updateProfile = async (profileData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.put(
    `${url}/auth/profile/`,
    {
      phone: profileData.phone,
      subscribed: profileData.subscribed,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return res.data;
};

export const forgotPassword = async (email) => {
  const res = await axios.post(`${url}/auth/forgot-password/`, {
    email,
  });
  return res.data;
};

export const resetPassword = async (token, newPassword, email) => {
  const res = await axios.post(`${url}/auth/reset-password/`, {
    reset_code: token,
    new_password: newPassword,
    email: email,
  });
  return res.data;
};

export const updatePassword = async (data) => {
  const token = localStorage.getItem("accessToken");

  const response = await axios.post(`${url}/auth/change-password/`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });

  return response.data;
};
