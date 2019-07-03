CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL
);
-- isbn,title,author,year
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
    
);
-- 
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY, 
    review VARCHAR NOT NULL,
    user_id  INTEGER REFERENCES users,
    book_id INTEGER REFERENCES books
);
-- JOIN
-- SELECT title, author, year, average_score FROM books JOIN reviews ON reviews.book_id = books.id; 
