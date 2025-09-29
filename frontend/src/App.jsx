import HomePage from "./pages/HomePage/HomePage";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MoviePage from "./pages/HomePage/MoviePage";
import SearchPage from "./pages/SearchPage/SearchPage";
import BookingPage from "./pages/BookingPage/BookingPage";

function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/movie/:id" element={<MoviePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/booking/:id/:showtime" element={<BookingPage />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
