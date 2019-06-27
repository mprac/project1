import csv
import psycopg2

# Set up database
conn = psycopg2.connect('postgres://kwyjwpagxkxzos:2478e5bd82e240fa0f60b08d9646410d8a7e4f81849bdb20eff61e44dca65958@ec2-54-83-192-245.compute-1.amazonaws.com:5432/d6oqcei069ga26')
cur = conn.cursor()

with open("books.csv") as booksfile:
    bookreader = csv.DictReader(booksfile)

    for row in bookreader:
        cur.execute('INSERT INTO books (isbn,title,author,year) VALUES (%s,%s,%s,%s)', (row["isbn"],row["title"],row["author"],row["year"]))
            
        conn.commit()
    cur.close()
    conn.close()
