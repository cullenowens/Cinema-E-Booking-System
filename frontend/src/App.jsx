import HomePage from "./pages/HomePage/HomePage";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MoviePage from "./pages/HomePage/MoviePage";
import SearchPage from "./pages/SearchPage/SearchPage";
import BookingPage from "./pages/BookingPage/BookingPage";
import SignInPage from "./pages/SignInPage/SignInPage";
import RegisterPage from "./pages/RegisterPage/RegisterPage";
import { AuthProvider } from "./contexts/AuthContext";
import VerifyPage from "./pages/VerifyPage/VerifyPage";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/movie/:id" element={<MoviePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/booking/:id/:showtime" element={<BookingPage />} />
          <Route path="/verify" element={<VerifyPage />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
