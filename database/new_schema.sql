-- -
-- Table structure for table `Genre_List`
-- 

CREATE TABLE IF NOT EXISTS `Genre_List` (
  `genre_id` int NOT NULL AUTO_INCREMENT,
  `genre_name` varchar(50) NOT NULL,
  PRIMARY KEY (`genre_id`),
  UNIQUE KEY `genre_name` (`genre_name`)
);


-- Table structure for table `Movie_Genres`

CREATE TABLE IF NOT EXISTS `Movie_Genres` (
  `movie_id` int NOT NULL,
  `genre_id` int NOT NULL,
  PRIMARY KEY (`movie_id`,`genre_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `Movie_Genres_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `Movies` (`movie_id`) ON DELETE CASCADE,
  CONSTRAINT `Movie_Genres_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `Genre_List` (`genre_id`) ON DELETE CASCADE
);


-- Table structure for table `Movie_Showtimes`

CREATE TABLE IF NOT EXISTS  `Movie_Showtimes` (
  `movie_id` int NOT NULL,
  `showtime_id` int NOT NULL AUTO_INCREMENT,
  `showtime_value` time NOT NULL,
  PRIMARY KEY (`showtime_id`),
  KEY `movie_id` (`movie_id`),
  CONSTRAINT `Movie_Showtimes_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `Movies` (`movie_id`) ON DELETE CASCADE
);


-- Table structure for table `Movies`

CREATE TABLE IF NOT EXISTS  `Movies` (
  `movie_id` int NOT NULL AUTO_INCREMENT,
  `movie_title` varchar(255) NOT NULL,
  `movie_description` text,
  `age_rating` varchar(10) DEFAULT NULL,
  `poster_url` varchar(255) DEFAULT NULL,
  `trailer_url` varchar(255) DEFAULT NULL,
  `movie_status` enum('Coming Soon','Currently Running') NOT NULL,
  PRIMARY KEY (`movie_id`)
);


-- Table structure for table `auth_permission`

CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
); 



-- Table structure for table `auth_user`

CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
);

-- Table structure for table `auth_user_user_permissions`

CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
); 


-- Table structure for table `cinema_address`

CREATE TABLE IF NOT EXISTS `cinema_address` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `street` varchar(100) NOT NULL,
  `city` varchar(50) NOT NULL,
  `state` varchar(50) NOT NULL,
  `zip_code` varchar(10) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `cinema_address_user_id_de445a3f_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
); 


-- Table structure for table `cinema_paymentcard`

CREATE TABLE IF NOT EXISTS `cinema_paymentcard` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `brand` varchar(20) NOT NULL,
  `expiration` varchar(7) NOT NULL,
  `card_number_enc` varchar(256) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cinema_paymentcard_user_id_aa84df0a_fk_auth_user_id` (`user_id`),
  CONSTRAINT `cinema_paymentcard_user_id_aa84df0a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
);


-- Table structure for table `cinema_profile`

CREATE TABLE IF NOT EXISTS `cinema_profile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `phone` varchar(20) NOT NULL,
  `subscribed` tinyint(1) NOT NULL,
  `status` varchar(10) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `cinema_profile_user_id_f927fc0d_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
);


-- Table structure for table `cinema_promotions`

CREATE TABLE IF NOT EXISTS `cinema_promotions` (
  `promo_id` int NOT NULL AUTO_INCREMENT,
  `discount` decimal(5,2) NOT NULL,
  `promo_code` varchar(100) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`promo_id`),
  UNIQUE KEY `promo_code` (`promo_code`)
); 

-- Table structure for table `cinema_user_optins`

CREATE TABLE IF NOT EXISTS `cinema_user_optins` (
  `user_id` int NOT NULL,
  `promo_opt_in` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`user_id`),
  CONSTRAINT `cinema_user_optins_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
); 

-- Table structure for table `cinema_user_promos`

CREATE TABLE IF NOT EXISTS `cinema_user_promos` (
  `user_id` int NOT NULL,
  `promo_id` int NOT NULL,
  `sent_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `redeemed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`user_id`,`promo_id`),
  KEY `promo_id` (`promo_id`),
  CONSTRAINT `cinema_user_promos_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cinema_user_promos_ibfk_2` FOREIGN KEY (`promo_id`) REFERENCES `cinema_promotions` (`promo_id`) ON DELETE CASCADE
); 

-- Table structure for table `cinema_verificationtoken`

CREATE TABLE IF NOT EXISTS `cinema_verificationtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` char(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `cinema_verificationtoken_user_id_d12df1ce_fk_auth_user_id` (`user_id`),
  CONSTRAINT `cinema_verificationtoken_user_id_d12df1ce_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
); 

-- Table structure for table `django_admin_log`

CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
); 

-- Table structure for table `django_content_type`

CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
); 

-- Table structure for table `django_migrations`

CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
);

-- Table structure for table `django_session`

CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
); 

-- Table for showrooms
CREATE TABLE IF NOT EXISTS showrooms (
	showroom_id INT AUTO_INCREMENT PRIMARY KEY,
    showroom_name VARCHAR(50) NOT NULL
);

-- table for all seats (format: A1, B17, etc)
CREATE TABLE IF NOT EXISTS seats (
	seat_id INT AUTO_INCREMENT PRIMARY KEY,
    showroom_id INT NOT NULL,
    row_label CHAR(1) NOT NULL,	-- A, B, C etc
    seat_number INT NOT NULL,	
    FOREIGN KEY (showroom_id) REFERENCES showrooms(showroom_id),
    UNIQUE (showroom_id, row_label, seat_number)
);

-- table for showings (movie at a specific time at a specific showroom)
CREATE TABLE IF NOT EXISTS showings (
    showing_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    showroom_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (showroom_id) REFERENCES showrooms(showroom_id),
    UNIQUE (showroom_id, start_time)
);

-- table for bookings (when a user books tickets)
CREATE TABLE IF NOT EXISTS bookings (
	booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

-- table for singular tickets
CREATE TABLE IF NOT EXISTS tickets (
	ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    showing_id INT NOT NULL,
    seat_id INT NOT NULL,
    age_category ENUM('Child','Adult','Senior') NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (showing_id) REFERENCES showings(showing_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id)
);