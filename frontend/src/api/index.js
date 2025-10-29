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
