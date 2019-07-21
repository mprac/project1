import os
#import psycopg2
import requests

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy.exc import IntegrityError
#from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "fksjdnfksdnfiwnfimbj3249vidunv"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database in .env
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
def index():
    if 'user' in session:
        username = session['user']
        ## BEGIN SEARCH ##
        if request.method == "POST":
            search = "%" + str(request.form.get("search")).title() + "%"
            if search:
                results = db.execute("SELECT * FROM books WHERE title LIKE :title or isbn LIKE :isbn or author LIKE :author LIMIT 20", {"title":search,"isbn":search,"author":search})
                if results.rowcount == 0:
                    return render_template('index.html', username=username, error="Your search returned no results")
                else:
                    return render_template('index.html', username=username, results=results)
            ## END SEARCH ##  
        return render_template('index.html', username=username)
    return redirect(url_for('login'))

########## Register - Login - Logout ##########
@app.route("/auth/register", methods=["GET", "POST"])
def register():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        encryptPass = generate_password_hash(password)
        
        try:
            db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)", {"email": email, "username": username, "password": encryptPass})
        except:
            return render_template("auth/register.html", message="email or username already exist")
        db.commit()               
        return render_template('auth/success.html')
    #if user is not in session render template    
    return render_template("auth/register.html") 

@app.route("/auth/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.execute('SELECT * FROM users WHERE email=:email', {'email':email}).fetchone()
        if user is None:
            message = 'No Such User'
        elif not check_password_hash(user.password, password):
            message = 'Invalid Password'
        else:
            session['user'] = user.username
            return redirect(url_for('index'))

        return render_template('auth/login.html', message=message)
    return render_template('auth/login.html')

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
########## END Register - Login - Logout ##########

########## Book Page Review Submissions ##########
@app.route("/book/<int:id>")
def book(id):
    if 'user' in session:
        username = session['user']
        book = db.execute('SELECT * FROM books WHERE id=:id', {'id':id}).fetchone()
        user_id = db.execute('SELECT id FROM users WHERE username=:username', {'username': username}).fetchone()
        reviews = db.execute('SELECT * FROM reviews JOIN users ON reviews.user_id = users.id')
        rating_average = db.execute('SELECT TRUNC(AVG(rating), 2) FROM reviews WHERE book_id=:id',{'id':id})
        # get goodreads ratings
        isbn = db.execute('SELECT isbn FROM books WHERE id=:id', {'id':id}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "eNLoXytUL2ZxAVY6gxVwEw", "isbns":isbn})
        gr_data = res.json()
        gr_average_rating = gr_data["books"][0]["average_rating"]
        gr_ratings_count = gr_data["books"][0]["ratings_count"]
        if book is None:
            return redirect(url_for('index'))
        return render_template('book.html', username=username,book=book,user_id=user_id, reviews=reviews, rating_average=rating_average, gr_average_rating=gr_average_rating, gr_ratings_count=gr_ratings_count)
    return redirect(url_for('index'))

@app.route("/review", methods=["POST", "GET"])
def review():
    if 'user' in session:
        username = session['user']
        if request.method == "POST":
            review = request.form.get('review')
            rating = request.form.get('rating')
            book_id = request.form.get('book_id')
            user_id = request.form.get('user_id')
            if rating > str(5) or rating < str(1):
                flash('error with review')
                return redirect(url_for('book', id=book_id))
            reviewed = db.execute('SELECT * FROM reviews WHERE user_id=:user_id and book_id=:book_id',{'user_id': user_id,'book_id': book_id}).fetchone()
            if reviewed:
                flash('you already reviewed this book')
                return redirect(url_for('book', id=book_id))
            elif not review:
                flash('cannot submit empty review')
                return redirect(url_for('book', id=book_id))
            else:
                db.execute("INSERT INTO reviews (review, rating, book_id, user_id) VALUES (:review, :rating, :book_id, :user_id)", {"review": review,"rating": rating, "book_id": book_id, "user_id": user_id})
                db.commit()

                flash('your review is submitted')
                return redirect(url_for('book', id=book_id))
    return redirect(url_for('index'))           

########## END Book Page Review Submissions ##########
########## Begin API book review ##########
@app.route('/api/<isbn>', methods=["GET"])
def goodreadsapi(isbn):
    if 'user' in session:
        username = session['user']
        if request.method == "GET":
            book = db.execute('SELECT * FROM books WHERE isbn=:isbn', {'isbn':isbn}).fetchone()
            average_score = db.execute('SELECT TRUNC(AVG(rating), 2) FROM reviews JOIN books ON reviews.book_id = books.id AND isbn=:isbn', {'isbn':isbn}).fetchone()
            review_count = db.execute('SELECT COUNT(rating) FROM reviews JOIN books ON reviews.book_id = books.id AND isbn=:isbn', {'isbn':isbn})
            if book is None:
                return render_template('404.html'), 404
            for row in average_score:
                if row:
                    score = float(row)
                else:
                    score = 0
            for row in review_count:
                if row:
                    count = row[0]
                else:
                    count = 0
            return jsonify({
                "title": book.title,
                "author": book.author,
                "year": book.year,
                "isbn": book.isbn,
                "average_score": score,
                "review_count": count
            })
    return redirect(url_for('login'))
        
        
  
