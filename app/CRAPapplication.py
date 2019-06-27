import os
import requests

from flask import Flask, session, render_template, jsonify, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

# Check for environment variable in .env file
#.env file stores database url to heroku and sets up all imports
if not os.getenv("DATABASE_URL"): 
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

########## INDEX ##########
@app.route("/")
def index():
   
    if 'user' in session:
        # res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "eNLoXytUL2ZxAVY6gxVwEw", "isbns": "9781632168146"})
        # data = jsonify(res.json())
        #return jsonify(data)

        #Assigne username variable to pass to html view
        username = session['user']

        return render_template('index.html', username=username)
    return redirect(url_for('login'))

########## REGISTER ROUTE ##########
@app.route("/auth/register", methods=["GET", "POST"])
def register():
    #check if the user is in session
    if 'user' in session:
        return redirect(url_for('index'))

    #check if it was a get request. if not then it is a post. 
    if request.method == "GET":
        return render_template('auth/register.html')

    #Get form information from post request
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    encryptPass = generate_password_hash(password)

    #insert the form information into the database
    #username and email fields are unique and will return a error
    #if error is returned the message will be returned and rendered to the view
    try:
        db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)", {"email": email, "username": username, "password": encryptPass})
    except:
        return render_template("auth/register.html", message="Email or username already exist")
    

    #if the user registers successfully then add user to the session
    #show success message
    #session['user'] = db.execute('SELECT username FROM users WHERE email= :email', {"email": email}).fetchone()
    return render_template("auth/success.html")

########## LOGIN ROUTE ##########
@app.route('/auth/login', methods=["GET", "POST"])
def login():
    #check if user is in session
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        user = db.execute("SELECT id, password FROM users WHERE email= :email", {"email": email}).fetchone()

        if db.execute("SELECT * FROM users WHERE email=:email",{'email':email}).rowcount==0 or check_password_hash(user.password, password) == False:
            render_template("auth/login.html", message="username or password did not match please try again!")
        else:
            username = db.execute('SELECT username FROM users WHERE email= :email', {"email": email}).fetchone()
            db.commit()

            session['user'] = username
            return redirect(url_for('index'))

    #response to a get request
    return render_template("auth/login.html")


########## LOGOUT ROUTE ##########
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    index()