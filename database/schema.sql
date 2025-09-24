-- Movie Details
CREATE TABLE IF NOT EXISTS Movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,	-- initialize movie id 
    movie_title VARCHAR(255) NOT NULL,
    movie_description TEXT,
    age_rating VARCHAR(10),		-- G, PG, etc
    poster_url VARCHAR(255),
    trailer_url VARCHAR(255),	
    movie_status ENUM('Coming Soon', 'Currently Running') NOT NULL	
);

-- Stores movie genres
CREATE TABLE IF NOT EXISTS Genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,	-- initialize genre 
    genre_name VARCHAR(50) NOT NULL UNIQUE	-- cannot have multiple genres w/ same name
);

-- Links movies to genres
CREATE TABLE IF NOT EXISTS Movie_Genres (
    movie_id INT NOT NULL,	-- existing movie id
    genre_id INT NOT NULL,	-- existing genre id
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE
);

-- Hardcodes showtimes for movies
CREATE TABLE IF NOT EXISTS Movie_Showtimes (
	movie_id INT NOT NULL,	-- existing movie id
    showtime_id INT AUTO_INCREMENT PRIMARY KEY,		-- initialize showtime
    showtime_value TIME NOT NULL,	-- showtimes given as HH:MM:SS (24 hr)
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE
);