import os
import psycopg2

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    if 'user' in session:
        username = session['user']
        ## BEGIN SEARCH ##
        # conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        # cur = conn.cursor()
        search = "%" + str(request.form.get("search")).title() + "%"
        cur.execute("SELECT * FROM books WHERE title LIKE %s OR isbn LIKE %s OR author LIKE %s",(search,search,search,))
        results = cur.fetchall()
        ## END SEARCH ##   
        return render_template('index.html', username=username, results=results)
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
            db.commit()
        return render_template('auth/login.html', message=message)
    return render_template('auth/login.html')

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
########## END Register - Login - Logout ##########
