
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import os

import mysql.connector


# Creating the flask application object
app = Flask(__name__)

# Load environment variables
load_dotenv(verbose=True)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)








# Set up database connection
cnx = mysql.connector.connect(
    user=os.getenv("DATABASE_USERNAME"),
    host="localhost",
    password=os.getenv("DATABASE_PASSWORD"),
    database=os.getenv("DATABASE_NAME")
)


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/search")
def search():
    cursor = cnx.cursor()

    search = request.args.get("q")
    if search is None:
        query = "SELECT * FROM product"
    else:
        query = f"SELECT * FROM product WHERE name LIKE '%{search}%'"

    # Execute a query
    cursor.execute(query)

    # Fetch the results
    # converting to list to fully exhaust the generator before closing the cursor
    results = list(cursor.fetchall())

    # Close the cursor and connection
    cursor.close()

    return render_template('search.html', rows=results)



@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        
        if not request.form.get('username'):
            return render_template('login.html', error='Please enter your username')
        elif not request.form.get('password'):
            return render_template('login.html', error='Please enter your password')
        
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get('username'),))
        user = cursor.fetchone()
        cursor.close()

        if user is None:
            return render_template('login.html', error='Invalid username')
        elif not check_password_hash(user[2], request.form.get('password')):
            return render_template('login.html', error='Invalid password')
        
        session['user_id'] = user[0]
        return redirect('/')

    else:
        return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()

    if request.method == 'POST':
        if not request.form.get('username'):
            return render_template('register.html', error='Please enter your username')
        
        elif not request.form.get('password'):
            return render_template('register.html', error='Please enter your password')
        
        elif not request.form.get('confirmation'):
            return render_template('register.html', error='Please confirm your password')
        
        elif request.form.get('password') != request.form.get('confirmation'):
            return render_template('register.html', error='Passwords do not match')
        
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get('username'),))
        user = cursor.fetchone()
        cursor.close()

        if user is not None:
            return render_template('register.html', error='Username already exists')
        
        password = request.form.get('password')
        for i in password:
            if i == ' ':
                return render_template('register.html', error="password doesn't meet the requirements")

        for i in password:
            if i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                break
        else:
            return render_template('register.html', error="password doesn't meet the requirements")

        for i in password:
            if i in '1234567890':
                break
        else:
            return render_template('register.html', error="password doesn't meet the requirements")

        for i in password:
            if (ord(i)>32 and ord(i)<48) or (ord(i)>57 and ord(i)<65) or (ord(i)>90 and ord(i)<97) or (ord(i)>122 and ord(i)<127):
                break
        else:
            return render_template('register.html', error="password doesn't meet the requirements")
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (request.form.get('username'), password))
        cnx.commit()

        cursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get('username'),))
        user = cursor.fetchone()

        session['user_id'] = user[0]
        return redirect('/')

    else:
        return render_template('register.html')

