import csv
import psycopg2

# Set up database
conn = psycopg2.connect('postgres://ldwrrbquqpqove:b5b961aad49e1d2dc77d9e4f8ee9f9adf2a4c57791ec67599505dfbc8959eb82@ec2-52-71-85-210.compute-1.amazonaws.com:5432/d6ea6ijeqt6peu')
cur = conn.cursor()

with open("books.csv") as booksfile:
    bookreader = csv.DictReader(booksfile)

    for row in bookreader:
        cur.execute('INSERT INTO books (isbn,title,author,year) VALUES (%s,%s,%s,%s)', (row["isbn"],row["title"],row["author"],row["year"]))
            
        conn.commit()
    cur.close()
    conn.close()
