import os
import requests

from flask import Flask, session, render_template, jsonify, request, redirect, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_login import LoginManager, login_user, login_required, logout_user, confirm_login
from sqlalchemy.exc import IntegrityError
from .forms import RegisterForm


app = Flask(__name__)
app.secret_key =  b'++\xd4\xe0\xe1z\x16\xa6\xbf\xf7\xc2PvW\xce\xd4'

# Check for environment variable in .env file
if not os.getenv("DATABASE_URL"): 
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if 'user' in session:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "eNLoXytUL2ZxAVY6gxVwEw", "isbns": "9781632168146"})
        
        data = jsonify(res.json())
        #return jsonify(data)
        return render_template('index.html', data=data)
    return redirect(url_for('login'))

#register the user
@app.route("/auth/register", methods=["GET", "POST"])
def register():
    if 'user' in session:
        return redirect(url_for('index'))
    # used generate a csrf token to protect the form
    form = RegisterForm()
    print(form.errors)
    
    if request.method == "GET":
        return render_template('auth/register.html', form=form)

    #get form information
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    encryptPass = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)", {"email": email, "username": username, "password": encryptPass})
    except IntegrityError:
        db.rollback()
        return render_template("auth/register.html", message="Email or username already exist", form=form)
    db.commit()
    session['user'] = request.form['username']
    return render_template("auth/success.html")


@app.route('/auth/login', methods=["GET", "POST"])
def login():  
    if request.method == "POST":
        email=request.form.get("email")
        password=request.form.get("password")
        user = db.execute("SELECT id, password FROM users WHERE email= :email", {"email": email}).fetchone()

        if db.execute("SELECT * FROM users WHERE email=:email",{'email':email}).rowcount==0 or check_password_hash(user.password, password)==True: 
            flash(f'{email} you are now logged in')
            session['user'] = request.form['email']
            return redirect(url_for('index'))
        else:
            return render_template("auth/login.html", message="username or password did not match please try again!") 
    return render_template("auth/login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    index()