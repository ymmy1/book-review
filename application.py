import os

import requests

from flask import Flask, flash, jsonify, redirect, render_template, request, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up json
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "lH3Sp0wTfhoxMdREQYZw", "isbns": "9781632168146"})
# print(res.json())

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Creating users, books and reviews
db.execute("CREATE TABLE IF NOT EXISTS users(id serial PRIMARY KEY NOT NULL,username VARCHAR (10) UNIQUE NOT NULL,nickname VARCHAR (10) UNIQUE NOT NULL,hash VARCHAR (150) NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS books(id serial PRIMARY KEY NOT NULL,isbn VARCHAR (10) UNIQUE NOT NULL,title VARCHAR (40) UNIQUE NOT NULL,author VARCHAR (40) NOT NULL,year INTEGER NOT NULL )")
db.commit()


@app.route("/")
@login_required
def index():
    
    # Random books
    row1 = db.execute("SELECT * FROM books WHERE random() < 0.01 limit 5;").fetchall()
    row2 = db.execute("SELECT * FROM books WHERE random() < 0.01 limit 5;").fetchall()

    return render_template("index.html",  row1=row1, row2=row2) 

@app.route("/<int:id>")
def book(id):
        
    # error handling
    if not book:
        return render_template("index.html",  message="404. No such book with this ID :(")

    return render_template("book_info.html",  book=book)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        username=request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE (username = :username)",
                            {"username": username}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_nickname"] = rows[0]["nickname"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
        
    # Query database for username
    username=request.form.get("username")
    rows = db.execute("SELECT * FROM users WHERE (username = :username)",
                            {"username": username}).fetchall()

    if len(rows) != 0 :
        return apology("this username is taken :(", 403)

    pas1 = request.form.get("password")
    pas2 = request.form.get("confirmPassword")
    if pas1 != pas2:
        # Reset passwords
        pas1 = ""
        pas2 = ""
        return apology("passwords don't match", 403)

    # Reset passwords
    pas1 = ""
    pas2 = ""

    nickname=request.form.get("nickname")
    rows = db.execute("SELECT * FROM users WHERE (nickname = :nickname)",
                            {"nickname": nickname}).fetchall()

    if len(rows) != 0 :
        return apology("this nickname is taken :(", 403)

    password=generate_password_hash(request.form.get("password"))
    db.execute("INSERT INTO users (username, nickname, hash) VALUES(:username, :nickname, :password)",
                {"username": username, "nickname": nickname, "password": password})
    db.commit()

    # Redirect user to login page
    return redirect("/login")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/search", methods=["POST"])
def search():
    # requesting the text from search
    message = request.form.get("search")
    message = "".join(("%", message, "%"))

    t_search = db.execute("SELECT * FROM books WHERE title ILIKE :msg", {"msg": message}).fetchall()
    a_search = db.execute("SELECT * FROM books WHERE author ILIKE :msg", {"msg": message}).fetchall()

    # Total number of books
    total = int(len(t_search)) + int(len(a_search))
    return render_template("search.html",   t_search=t_search, a_search=a_search, total=total)