import psycopg2

# Set up database
conn = psycopg2.connect('postgres://kwyjwpagxkxzos:2478e5bd82e240fa0f60b08d9646410d8a7e4f81849bdb20eff61e44dca65958@ec2-54-83-192-245.compute-1.amazonaws.com:5432/d6oqcei069ga26')
cur = conn.cursor()
user_input = input('search value')
search = "%" + str(user_input).title() + "%"
cur.execute("SELECT * FROM books WHERE title LIKE %s OR isbn LIKE %s OR author LIKE %s", (search,search,search,))
for record in cur:
    print(record)
