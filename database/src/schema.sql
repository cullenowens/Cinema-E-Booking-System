

-- Stores core movie information
CREATE TABLE IF NOT EXISTS Movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    rating VARCHAR(10), -- e.g., 'PG-13', 'R'
    release_date DATE,
    duration_minutes INT,
    poster_url VARCHAR(255),
    trailer_url VARCHAR(255),
    status ENUM('Coming Soon', 'Currently Running', 'Archived') NOT NULL
);

-- Stores movie genres for filtering
CREATE TABLE IF NOT EXISTS Genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Links movies to genres (many-to-many relationship)
CREATE TABLE IF NOT EXISTS Movie_Genres (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE
);


-- Stores user and admin account information
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Always store hashed passwords!
    phone_number VARCHAR(20),
    role ENUM('Customer', 'Admin') NOT NULL DEFAULT 'Customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Defines the theater rooms
CREATE TABLE IF NOT EXISTS Showrooms (
    showroom_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    capacity INT NOT NULL
);

-- The main schedule, linking a movie, a room, and a time
CREATE TABLE IF NOT EXISTS Showings (
    showing_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT,
    showroom_id INT,
    show_time DATETIME NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (showroom_id) REFERENCES Showrooms(showroom_id) ON DELETE CASCADE
);



-- Represents a completed user order
CREATE TABLE IF NOT EXISTS Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    showing_id INT,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_price DECIMAL(10, 2) NOT NULL,
    -- promotion_id could be added later
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (showing_id) REFERENCES Showings(showing_id)
);

-- Defines individual seats in a showroom
CREATE TABLE IF NOT EXISTS Seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    showroom_id INT,
    row_char CHAR(1) NOT NULL,
    seat_number INT NOT NULL,
    UNIQUE(showroom_id, row_char, seat_number),
    FOREIGN KEY (showroom_id) REFERENCES Showrooms(showroom_id) ON DELETE CASCADE
);

-- Represents a single ticket in a booking, linked to a specific seat
CREATE TABLE IF NOT EXISTS Tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    seat_id INT,
    ticket_type ENUM('Adult', 'Child', 'Senior') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES Seats(seat_id)
);

SHOW TABLES;