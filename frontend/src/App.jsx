import HomePage from "./pages/HomePage/HomePage";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MoviePage from "./pages/HomePage/MoviePage";
import SearchPage from "./pages/SearchPage/SearchPage";
import BookingPage from "./pages/BookingPage/BookingPage";
import SignInPage from "./pages/SignInPage/SignInPage";
import RegisterPage from "./pages/RegisterPage/RegisterPage";
import { AuthProvider } from "./contexts/AuthContext";
import VerifyPage from "./pages/VerifyPage/VerifyPage";
import ProfilePage from "./pages/ProfilePage/ProfilePage";
import PaymentPage from "./pages/PaymentPage/PaymentPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage/ForgotPasswordPage";
import AdminPage from "./pages/AdminPage/AdminPage";
import ManageMoviesPage from "./pages/ManageMoviesPage/ManageMoviesPage";
import ManageShowtimesPage from "./pages/ManageShowtimesPage/ManageShowtimesPage";
import ManagePromotionsPage from "./pages/ManagePromotionsPage/ManagePromotionsPage";
import ManageUsersPage from "./pages/ManageUsersPage/ManageUsersPage";

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
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/payment-methods" element={<PaymentPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/admin/manage-movies" element={<ManageMoviesPage />} />
          <Route
            path="/admin/manage-promotions"
            element={<ManagePromotionsPage />}
          />
          <Route path="/admin/manage-users" element={<ManageUsersPage />} />

          <Route
            path="/admin/manage-showtimes"
            element={<ManageShowtimesPage />}
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
