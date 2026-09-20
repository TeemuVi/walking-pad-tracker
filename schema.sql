CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);
CREATE TABLE walks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    minutes_walked INTEGER,
    distance REAL,
    steps INTEGER,
    time_stamp TEXT
);