
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import os

from app.helpers import login_required, admin_login_required

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

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response





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
        session['user_email'] = user['email']
        session['username'] = user['first_name']
        return redirect('/')

    else:
        return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO check if the user is a customer or supplier
    session.clear()

    if request.method == 'POST':
        if not request.form.get('first_name'):
            return render_template('register.html', error='Please enter your first name')
        
        elif not request.form.get('email'):
            return render_template('register.html', error='Please enter your email')
        
        elif not request.form.get('password'):
            return render_template('register.html', error='Please enter your password')
        
        elif not request.form.get('re_password'):
            return render_template('register.html', error='Please confirm your password')
        
        elif not request.form.get('phone_no'):
            return render_template('register.html', error='Please enter your phone number')
        
        elif not request.form.get('age'):
            return render_template('register.html', error='Please enter your age')
        
        elif not request.form.get('address'):
            return render_template('register.html', error='Please enter your address')
        
        elif not request.form.get('address2'):
            return render_template('register.html', error='Please enter your address')
        
        elif not request.form.get('city'):
            return render_template('register.html', error='Please enter your city')
        
        elif not request.form.get('state'):
            return render_template('register.html', error='Please enter your state')
        
        elif not request.form.get('zip'):
            return render_template('register.html', error='Please enter your zip code')
        
        elif request.form.get('password') != request.form.get('re_password'):
            return render_template('register.html', error='Passwords do not match')

        utype = request.form['RegisterRadio']


        cursor = cnx.cursor()
        if utype == 'customer':
            cursor.execute("SELECT * FROM customer WHERE email = %s", (request.form.get('email'),))
        elif utype == 'supplier':
            cursor.execute("SELECT * FROM supplier WHERE email = %s", (request.form.get('email'),))
        elif utype == 'delivery_agent':
            cursor.execute("SELECT * FROM delivery_agent WHERE email = %s", (request.form.get('email'),))

        user = cursor.fetchone()
        cursor.close()

        if user is not None:
            return render_template('register.html', error='Email already exists')
        
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
            cursor.execute("SELECT MAX(phoneID) FROM phone_number")
            phoneID = cursor.fetchone()
            cursor.execute("INSERT INTO phone_number (num, phoneID) VALUES (%s, %s)", (request.form.get('phone_no'), int(phoneID['MAX(phoneID)'])+1))
            cursor.execute("INSERT INTO address (street_name, apt_number, city, state, zip, country) VALUES (%s, %s, %s, %s, %s, %s)", (request.form.get('address'), request.form.get('address2'), request.form.get('city'), request.form.get('state'), request.form.get('zip'), request.form.get('country')))
            cursor.execute("SELECT MAX(addressID) FROM address")
            addressID = cursor.fetchone()
            cursor.execute("INSERT INTO customer (first_name, middle_initial, last_name, age, email, pwd, addressID, phoneID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (request.form.get('first_name'), request.form.get('middle_initial'), request.form.get('last_name'), request.form.get('age'), request.form.get('email'), generate_password_hash(request.form.get('password')), addressID['MAX(addressID)'], int(phoneID["MAX(phoneID)"]) + 1) )

        elif utype == 'supplier':
            cursor.execute("INSERT INTO address (street_name, apt_number, city, state, zip, country) VALUES (%s, %s, %s, %s, %s, %s)", (request.form.get('address'), request.form.get('address2'), request.form.get('city'), request.form.get('state'), request.form.get('zip'), request.form.get('country')))
            cursor.execute("SELECT MAX(addressID) FROM address")
            addressID = cursor.fetchone()
            cursor.execute("INSERT INTO supplier (first_name, middle_initial, last_name, email, pwd, addressID) VALUES (%s, %s, %s, %s, %s, %s)", (request.form.get('first_name'), request.form.get('middle_initial'), request.form.get('last_name'), request.form.get('email'), generate_password_hash(request.form.get('password')), addressID['MAX(addressID)']))
            
        elif utype == 'delivery_agent':
            cursor.execute("SELECT MAX(phoneID) FROM phone_number")
            phoneID = cursor.fetchone()
            cursor.execute("INSERT INTO phone_number (num, phoneID) VALUES (%s, %s)", (request.form.get('phone_no'), int(phoneID['MAX(phoneID)'])+1))
            cursor.execute("INSERT INTO delivery_agent (first_name, middle_initial, last_name, email, pwd, phoneID) VALUES (%s, %s, %s, %s, %s, %s)", (request.form.get('first_name'), request.form.get('middle_initial'), request.form.get('last_name'), request.form.get('email'), generate_password_hash(request.form.get('password')), int(phoneID['MAX(phoneID)'])+1))
        cnx.commit()

        if utype == 'customer':
            cursor.execute("SELECT * FROM customer WHERE email = %s", (request.form.get('email'),))
            user = cursor.fetchone()

            session['user_id'] = user['customerID']
            session['user_type'] = 'customer'
            session['user_email'] = user['email']
            session['username'] = user['first_name']
        elif utype == 'supplier':
            cursor.execute("SELECT * FROM supplier WHERE email = %s", (request.form.get('email'),))
            user = cursor.fetchone()

            session['user_id'] = user['supplierID']
            session['user_type'] = 'supplier'
            session['user_email'] = user['email']
            session['username'] = user['first_name']

        elif utype == 'delivery_agent':
            cursor.execute("SELECT * FROM delivery_agent WHERE email = %s", (request.form.get('email'),))
            user = cursor.fetchone()

            session['user_id'] = user['daID']
            session['user_type'] = 'delivery_agent'
            session['user_email'] = user['email']
            session['username'] = user['first_name']
        
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

        session['user_id'] = user['adminID']
        session['user_type'] = 'admin'
        session['username'] = user['username']
        return redirect('/admin')

    else:
        return render_template('adminlogin.html')


@app.route('/admin', methods=['GET'])
@admin_login_required
def admin():
    print(session)
    if session.get('user_type') != 'admin':
        return redirect('/adminlogin')

    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS n FROM customer")
    customer_count = cursor.fetchone()["n"]

    cursor.execute("SELECT COUNT(*) AS n FROM supplier")
    supplier_count = cursor.fetchone()["n"]

    cursor.execute("SELECT COUNT(*) AS n FROM delivery_agent")
    da_count = cursor.fetchone()["n"]

    return render_template('admin.html', customer_count=customer_count, supplier_count=supplier_count, da_count=da_count)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/account', methods=['GET'])
@login_required
def account():

    if session.get('user_type') == 'customer':
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer WHERE customerID = %s", (session.get('user_id'),))
        user = cursor.fetchone()
        cursor.close()
        return render_template('account_customer.html', user=user)
    elif session.get('user_type') == 'supplier':
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM supplier WHERE supplierID = %s", (session.get('user_id'),))
        user = cursor.fetchone()
        cursor.close()
        return render_template('account_supplier.html', user=user)
    elif session.get('user_type') == 'delivery_agent':
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM delivery_agent WHERE daID = %s", (session.get('user_id'),))
        user = cursor.fetchone()
        cursor.close()
        return render_template('account_da.html', user=user)
    else:
        return redirect('/login')


@app.route("/blog", methods=["GET", "POST"])
def blog():
    subbed = None
    if request.method == "POST":
        subbed = "You'll be notified as soon as the page has been constructed!"

    return render_template("blog.html", subbed=subbed)


@app.route("/account/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        return redirect("/account/cart/checkout")
    
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT p.name as n, c.quantity as q, p.price as pr FROM cart c JOIN product p on c.productID=p.productID WHERE c.customerID = %s", (session.get('user_id'),))
    cart = cursor.fetchall()
    cursor.close()

    # find cart total
    total = 0
    for item in cart:
        total += float(item["q"]) * float(item["pr"])

    return render_template("cart.html", cart=cart, total=round(total, 3))