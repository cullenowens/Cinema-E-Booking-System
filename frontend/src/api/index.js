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

export const getAllMovies = async () => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.get(`${url}/admin/movies/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const createMovie = async (movieData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.post(`${url}/admin/movies/create/`, movieData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const updateMovie = async (movieId, movieData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.put(`${url}/admin/movies/${movieId}/`, movieData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const deleteMovie = async (movieId) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.delete(`${url}/admin/movies/${movieId}/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const getGenres = async () => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.get(`${url}/admin/genres/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const getAdminShowings = async () => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.get(`${url}/admin/showings/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const getAdminShowrooms = async () => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.get(`${url}/admin/showrooms/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const createShowing = async (showingData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.post(`${url}/admin/showings/create/`, showingData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const updateShowing = async (id, showingData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.put(`${url}/admin/showings/${id}/`, showingData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const deleteShowing = async (id) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.delete(`${url}/admin/showings/${id}/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const checkShowingAvailability = async (
  showroom_id,
  start_time,
  end_time
) => {
  const token = localStorage.getItem("accessToken");
  const params = {
    showroom_id,
    start_time,
  };
  if (end_time) params.end_time = end_time;

  const res = await axios.get(`${url}/admin/showings/availability/`, {
    headers: { Authorization: `Bearer ${token}` },
    params: params,
  });
  return res.data;
};

export const getPromotions = async () => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.get(`${url}/admin/promotions/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const createPromotion = async (promoData) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.post(`${url}/admin/promotions/create/`, promoData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const deletePromotion = async (id) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.delete(`${url}/admin/promotions/${id}/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const sendPromotionEmail = async (id) => {
  const token = localStorage.getItem("accessToken");
  const res = await axios.post(
    `${url}/admin/promotions/${id}/send-email/`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  return res.data;
};
