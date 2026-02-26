-- TODO: 
-- Check Constraints [DONE]
-- on delete cascades 
-- Participation Constraints (do we need NOT NULLs? no right)

CREATE TABLE MotionPicture 
  (PRIMARY KEY INT id,
    VARCHAR(50) NAME,
    FLOAT rating CHECK (rating <= 10 AND rating >= 0), 
    VARCHAR(50) production, 
    INT budget CHECK (budget >= 0)
  );

CREATE TABLE Users 
(PRIMARY KEY VARCHAR(50) email,
  VARCHAR(50) name,
  INT age
);

CREATE TABLE Likes 
(INT mpid, VARCHAR(50) uemail, 
  PRIMARY KEY(mpid, uemail),
  FOREIGN KEY(mpid) REFERENCES(MotionPicture), 
  FOREIGN KEY(uemail) REFERENCES (Users)
);

CREATE TABLE Movie (INT mpid,
  FLOAT boxoffice_collection CHECK (boxoffice_collection >= 0),
  PRIMARY KEY(mpid),
  FOREIGN KEY(mpid) REFERENCES (MotionPicture)
);

CREATE TABLE Movie (
  INT mpid, 
  INT season_count CHECK (season_count >= 1),
  PRIMARY KEY(mpid),
  FOREIGN KEY(mpid) REFERENCES (MotionPicture)
);

CREATE TABLE People
(PRIMARY KEY INT id,
  VARCHAR(50) NAME,
  VARCHAR(10) nationality,
  VARCHAR(10) dob,
  VARCHAR(1) gender,
);


CREATE TABLE Role
(
  INT mpid,
  INT pid,
  VARCHAR(10) role_name,
  PRIMARY KEY (mpid, pid, role_name),
  FOREIGN KEY (mpid) REFERENCES (MotionPicture),
  FOREIGN KEY (pid) REFERENCES People,
);


CREATE TABLE Award
(
  INT mpid,
  INT pid,
  VARCHAR(50) award_name,
  INT award_year,
  PRIMARY KEY (mpid, pid, award_name, award_year),
  FOREIGN KEY (mpid) REFERENCES (MotionPicture),
  FOREIGN KEY (pid) REFERENCES People
);


CREATE TABLE Genre
(
  INT mpid,
  VARCHAR(50) genre_name,
  PRIMARY KEY (mpid, genre_name),
  FOREIGN KEY (mpid) REFERENCES (MotionPicture),
);

CREATE TABLE Location
(
  INT mpid,
  INT zip,
  VARCHAR(50) city,
  PRIMARY KEY (mpid, zip),
  FOREIGN KEY (mpid) REFERENCES (MotionPicture),
);
