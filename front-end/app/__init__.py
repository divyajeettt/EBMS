
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





# print(os.environ)


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
    # TODO check if the user is a customer or supplier
    session.clear()

    if request.method == 'POST':
        
        if not request.form.get('username'):
            return render_template('login.html', error='Please enter your username')
        elif not request.form.get('password'):
            return render_template('login.html', error='Please enter your password')
        
        cursor = cnx.cursor(dictionary=True)
        if request.form['LoginRadio'] == 'customer':
            cursor.execute("SELECT * FROM customer WHERE email = %s", (request.form.get('username'),))
        elif request.form['LoginRadio'] == 'supplier':
            cursor.execute("SELECT * FROM supplier WHERE email = %s", (request.form.get('username'),))
        user = cursor.fetchone()
        cursor.close()

        if user is None:
            return render_template('login.html', error='Invalid username')
        elif not check_password_hash(user['pwd'], request.form.get('password')):
            return render_template('login.html', error='Invalid password')
        
        
        if request.form['LoginRadio'] == 'customer':
            session['user_id'] = user['customerID']
            session['user_type'] = 'customer'
        elif request.form['LoginRadio'] == 'supplier':
            session['user_id'] = user['supplierID']
            session['user_type'] = 'supplier'
        session['username'] = user['email']
        return redirect('/')

    else:
        return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO check if the user is a customer or supplier
    session.clear()

    if request.method == 'POST':
        
        if not request.form.get('username'):
            return render_template('register.html', error='Please enter your username')
        
        elif not request.form.get('password'):
            return render_template('register.html', error='Please enter your password')
        
        elif not request.form.get('re-password'):
            return render_template('register.html', error='Please confirm your password')
        
        elif request.form.get('password') != request.form.get('re-password'):
            return render_template('register.html', error='Passwords do not match')
        
        utype = request.form['RegisterRadio']
        

        cursor = cnx.cursor()
        if utype == 'customer':
            cursor.execute("SELECT * FROM customer WHERE email = %s", (request.form.get('username'),))
        elif utype == 'supplier':
            cursor.execute("SELECT * FROM supplier WHERE email = %s", (request.form.get('username'),))

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
        
        cursor = cnx.cursor(dictionary=True)
        if utype == 'customer':
            cursor.execute("INSERT INTO customer (email, pwd) VALUES (%s, %s)", (request.form.get('username'), password))
        elif utype == 'supplier':
            cursor.execute("INSERT INTO supplier (email, pwd) VALUES (%s, %s)", (request.form.get('username'), password))

        cnx.commit()

        if utype == 'customer':
            cursor.execute("SELECT * FROM customer WHERE email = %s", (request.form.get('username'),))
            user = cursor.fetchone()

            session['user_id'] = user['customerID']
            session['user_type'] = 'customer'
            session['user_email'] = user['email']
        elif utype == 'supplier':
            cursor.execute("SELECT * FROM supplier WHERE email = %s", (request.form.get('username'),))
            user = cursor.fetchone()

            session['user_id'] = user['supplierID']
            session['user_type'] = 'supplier'
            session['user_email'] = user['email']
        cursor.close()

        return redirect('/')

    else:
        return render_template('register.html')



@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    session.clear()

    if request.method == 'POST':
        if not request.form.get('username'):
            return render_template('adminlogin.html', error='Please enter your username')
        elif not request.form.get('password'):
            return render_template('adminlogin.html', error='Please enter your password')
        
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (request.form.get('username'),))
        user = cursor.fetchone()
        cursor.close()

        if user is None:
            return render_template('adminlogin.html', error='Invalid username')
        # TODO add a check_password_hash function here
        elif user['pwd'] != request.form.get('password'):
            return render_template('adminlogin.html', error='Invalid password')
        
        # print(user['adminID'])
        session['user_id'] = user['adminID']
        session['user_type'] = 'admin'
        session['username'] = user['username']
        return redirect('/admin')
    
    else:
        return render_template('adminlogin.html')
    

@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.html')



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")