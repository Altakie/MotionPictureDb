-- TODO: 
-- Check Constraints [DONE]
-- on delete cascades [DONE]
-- Participation Constraints (do we need NOT NULLs? no right)

CREATE TABLE MotionPicture 
(
  id INT PRIMARY KEY,
  NAME VARCHAR(50),
  rating FLOAT CHECK (rating <= 10 AND rating >= 0), 
  production VARCHAR(50), 
  budget INT CHECK (budget >= 0)
);

CREATE TABLE Users 
(
  email VARCHAR(50) PRIMARY KEY,
  name VARCHAR(50),
  age INT
);

CREATE TABLE Likes 
(
  mpid INT, 
  uemail VARCHAR(50), 
  PRIMARY KEY(mpid, uemail),
  FOREIGN KEY(mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE, 
  FOREIGN KEY(uemail) REFERENCES Users(email) ON DELETE CASCADE
);

CREATE TABLE Movie 
(
  mpid INT,
  boxoffice_collection FLOAT CHECK (boxoffice_collection >= 0),
  PRIMARY KEY(mpid),
  FOREIGN KEY(mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);

CREATE TABLE Series 
(
  mpid INT, 
  season_count INT CHECK (season_count >= 1),
  PRIMARY KEY(mpid),
  FOREIGN KEY(mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);

CREATE TABLE People
(
  id INT PRIMARY KEY,
  NAME VARCHAR(50),
  nationality VARCHAR(10),
  dob VARCHAR(10),
  gender VARCHAR(1)
);


CREATE TABLE Role
(
  mpid INT,
  pid INT,
  role_name VARCHAR(10),
  PRIMARY KEY (mpid, pid, role_name),
  FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
  FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE
);


CREATE TABLE Award
(
  mpid INT,
  pid INT,
  award_name VARCHAR(50),
  award_year INT,
  PRIMARY KEY (mpid, pid, award_name, award_year),
  FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
  FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE
);


CREATE TABLE Genre
(
  mpid INT,
  genre_name VARCHAR(50),
  PRIMARY KEY (mpid, genre_name),
  FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);

CREATE TABLE Location
(
  mpid INT,
  zip INT,
  city VARCHAR(50),
  country VARCHAR(10),
  PRIMARY KEY (mpid, zip),
  FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);
