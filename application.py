import os
import requests

from flask import Flask, session, render_template, jsonify, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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


@app.route("/")
def index():
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "eNLoXytUL2ZxAVY6gxVwEw", "isbns": "9781632168146"})
    
    data = jsonify(res.json())
    #return jsonify(data)
    return render_template('index.html', data=data)
    
    #print(res.json())

    # return "totodod"









@app.route("/auth/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('auth/register.html')
    










@app.route('/auth/login', methods=['POST'])
def login():
    user = get_user(request.form['username'])

    if user.check_password(request.form['password']):
        login_user(user)
        app.logger.info('%s logged in successfully', user.username)
        return redirect(url_for('index'))
    else:
        app.logger.info('%s failed to log in', user.username)
        abort(401)

