import axios from "axios";

const url = "http://127.0.0.1:8000/api/movies";

export const getCurrentMovies = async () => {
  const res = await axios.get(`${url}/currently_running`);
  return res.data;
};

export const getFutureMovies = async () => {
  const res = await axios.get(`${url}/coming-soon`);
  return res.data;
};

export const searchMovies = async (query) => {
  const res = await axios.get(`${url}/search/?q=${query}`);
  return res.data;
};
export const getMovieDetails = async (id) => {
  const res = await axios.get(`${url}/${id}`);
  return res.data;
};
