CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    is_active VARCHAR
);
-- isbn,title,author,year
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
    
);
-- 
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY, 
    review_count INTEGER NOT NULL,
    average_score FLOAT NOT NULL,
    book_id INTEGER REFERENCES books
);
-- JOIN
-- SELECT title, author, year, average_score FROM books JOIN reviews ON reviews.book_id = books.id; 
