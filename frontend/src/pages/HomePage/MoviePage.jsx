import React from "react";
import { useParams } from "react-router-dom";

const MoviePage = () => {
  const { id } = useParams();
  return <div>{id}</div>;
};

export default MoviePage;
