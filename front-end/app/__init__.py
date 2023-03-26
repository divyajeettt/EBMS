from flask import Flask, render_template, request, session, redirect, url_for, abort
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


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/search")
def search():
    search = request.args.get("q")
    query = "SELECT * FROM product"
    query += f" WHERE name LIKE '%{search}%'" if search else ""

    with cnx.cursor() as cursor:
        cursor.execute(query)
        results = list(cursor.fetchall())

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

        with cnx.cursor(dictionary=True) as cursor:
            if request.form['LoginRadio'] == 'customer':
                cursor.execute("SELECT * FROM customer WHERE email = %s", (request.form.get('username'),))
            elif request.form['LoginRadio'] == 'supplier':
                cursor.execute("SELECT * FROM supplier WHERE email = %s", (request.form.get('username'),))
            user = cursor.fetchone()

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


        with cnx.cursor() as cursor:
            if utype == 'customer':
                cursor.execute("SELECT * FROM customer WHERE email = %s", (request.form.get('email'),))
            elif utype == 'supplier':
                cursor.execute("SELECT * FROM supplier WHERE email = %s", (request.form.get('email'),))
            elif utype == 'delivery_agent':
                cursor.execute("SELECT * FROM delivery_agent WHERE email = %s", (request.form.get('email'),))
            user = cursor.fetchone()

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


        with cnx.cursor(dictionary=True) as cursor:
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

        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM admin WHERE username = %s", (request.form.get('username'),))
            user = cursor.fetchone()

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

    context = {}
    with cnx.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT COUNT(*) AS n FROM customer")
        context["customer_count"] = cursor.fetchone()["n"]

        cursor.execute("SELECT COUNT(*) AS n FROM supplier")
        context["supplier_count"] = cursor.fetchone()["n"]

        cursor.execute("SELECT COUNT(*) AS n FROM delivery_agent")
        context["da_count"] = cursor.fetchone()["n"]

        cursor.execute("SELECT COUNT(*) AS n FROM orders")
        context["order_count"] = cursor.fetchone()["n"]

        cursor.execute("SELECT COUNT(*) AS n FROM order_product")
        context["product_count"] = cursor.fetchone()["n"]

    for key in context:
        context[key] = round(context[key], -1)

    return render_template("admin.html", context=context)


@app.route("/admin/<string:page>", methods=["GET"])
@admin_login_required
def admin_stats(page: str):
    if session.get("user_type") != "admin":
        return redirect("/adminlogin")

    table = {
        "customer": "customer", "supplier": "supplier",
        "deliveryagent": "delivery_agent", "order": "orders", "product": "order_product"
    }.get(page)

    if table is None:
        abort(404)

    context = {}
    with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(f"SELECT COUNT(*) AS n FROM {table}")
        context["count"] = round(cursor.fetchone()["n"], -1)

        if page == "customer":
            cursor.execute("""
                SELECT
                    customer.customerID,
                    CONCAT(customer.first_name, ' ', customer.middle_initial, ' ', customer.last_name) AS name,
                    COUNT(orders.orderID) AS total_orders,
                    SUM(product.price * order_product.quantity) AS total_spent,
                    AVG(product.price * order_product.quantity) AS avg_spent
                FROM customer
                INNER JOIN orders ON customer.customerID = orders.customerID
                INNER JOIN order_product ON orders.orderID = order_product.orderID
                INNER JOIN product ON order_product.productID = product.productID
                GROUP BY customer.customerID
                ORDER BY total_spent DESC
                LIMIT 10
            """)
            context["top_rated"] = cursor.fetchall()

            cursor.execute("""
                SELECT
                    customer.customerID,
                    CONCAT(customer.first_name, ' ', customer.middle_initial, ' ', customer.last_name) AS name,
                    COUNT(orders.orderID) AS total_orders,
                    SUM(product.price * order_product.quantity) AS total_spent
                FROM customer
                INNER JOIN orders ON customer.customerID = orders.customerID
                INNER JOIN order_product ON orders.orderID = order_product.orderID
                INNER JOIN product ON order_product.productID = product.productID
                GROUP BY customer.customerID
                HAVING total_orders <= 10
                ORDER BY total_orders ASC
                LIMIT 10
            """)
            context["inactive"] = cursor.fetchall()

        elif page == "order":
            cursor.execute("""
                SELECT (delivery_date IS NULL) as status, COUNT(*) AS n
                FROM orders
                GROUP BY status
            """)
            context["order_status"] = cursor.fetchall()

            cursor.execute("""
                SELECT
                    YEAR(order_date) AS year,
                    QUARTER(order_date) AS quarter,
                    MONTH(order_date) AS month,
                    COUNT(orders.orderID) AS order_count,
                    SUM(price * order_product.quantity) AS revenue
                FROM
                    orders
                    JOIN order_product ON orders.orderID = order_product.orderID
                    JOIN product ON order_product.productID = product.productID
                WHERE orders.delivery_date IS NOT NULL
                GROUP BY year, quarter, month
                ORDER BY year DESC, month DESC
            """)
            context["order_trend"] = cursor.fetchall()
            context["month"] = {
                1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
            }

        elif page == "product":
            cursor.execute("""
                SELECT p.productID, p.name, p.price, SUM(op.quantity) AS quantity
                FROM order_product op, product p
                WHERE p.productID = op.productID
                GROUP BY p.productID
                ORDER BY quantity DESC
                LIMIT 10
            """)
            context["best_sellers"] = cursor.fetchall()

            cursor.execute("""
                SELECT p.productID, p.name, p.price, AVG(pr.rating) AS avg_rating
                FROM product_review pr, product p
                WHERE p.productID = pr.productID
                GROUP BY p.productID
                HAVING avg_rating >= 3.5
                ORDER BY avg_rating DESC
                LIMIT 10
            """)
            context["top_rated"] = cursor.fetchall()

        elif page == "supplier":
            cursor.execute("""
                SELECT
                    s.supplierID,
                    CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS name,
                    email,
                    AVG(pr.rating) AS avg_rating
                FROM supplier s, product_review pr, product prod
                WHERE (
                    SELECT AVG(pr.rating) FROM product_review pr, product p
                    WHERE p.productID = pr.productID AND p.supplierID = s.supplierID
                    GROUP BY p.supplierID
                ) > 3
                AND s.supplierID = prod.supplierID AND pr.productID = prod.productID
                GROUP BY s.supplierID
                ORDER BY avg_rating DESC
                LIMIT 10
            """)
            context["top_rated"] = cursor.fetchall()

            cursor.execute("""
            SELECT s.supplierID, CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS name, email
            FROM supplier s
            WHERE NOT EXISTS (
                SELECT * FROM product p
                WHERE p.supplierID = s.supplierID
            )
            LIMIT 10
            """)
            context["inactive"] = cursor.fetchall()

        elif page == "deliveryagent":
            cursor.execute("""
                SELECT
                    da.daID,
                    CONCAT(da.first_name, ' ', da.middle_initial, ' ', da.last_name) AS name,
                    email,
                    AVG(dr.rating) AS avg_rating
                FROM da_review dr, delivery_agent da
                WHERE da.daID = dr.daID
                GROUP BY da.daID
                ORDER BY avg_rating DESC
                LIMIT 10
            """)
            context["top_rated"] = cursor.fetchall()

            cursor.execute("""
                SELECT
                    da.daID,
                    CONCAT(da.first_name, ' ', da.middle_initial, ' ', da.last_name) AS name,
                    email,
                    COUNT(o.orderID) AS total_orders
                FROM delivery_agent da
                LEFT JOIN orders o ON da.daID = o.daID
                GROUP BY da.daID
                ORDER BY total_orders DESC
                LIMIT 10
            """)
            context["most_active"] = cursor.fetchall()

    return render_template(f"admin/{page}.html", context=context)


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

        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM customer WHERE customerID = %s", (session.get('user_id'),))
            user = cursor.fetchone()
        return render_template('customer.html', user=user)

    elif session.get('user_type') == 'supplier':
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM supplier WHERE supplierID = %s", (session.get('user_id'),))
            user = cursor.fetchone()

        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM product WHERE supplierID = %s", (session.get('user_id'),))
            products = cursor.fetchall()

        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("""SELECT
                product.name as product_name, SUM(order_product.quantity) AS total_quantity_sold,
                SUM(order_product.quantity * product.price) AS total_revenue
                FROM product
                INNER JOIN order_product ON product.productID = order_product.productID
                INNER JOIN orders ON order_product.orderID = orders.orderID
                WHERE product.supplierID = %s
                GROUP BY product.name;""", (session.get('user_id'),)
            )
            sales = cursor.fetchall()

        return render_template('account/supplier.html', user=user, products=products, sales=sales)

    elif session.get('user_type') == 'delivery_agent':
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM delivery_agent WHERE daID = %s", (session.get('user_id'),))
            user = cursor.fetchone()

        return render_template('account/deliveryagent.html', user=user)

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
    cursor.execute("SELECT p.productID as i, p.name as n, c.quantity as q, p.price as pr FROM cart c JOIN product p on c.productID=p.productID WHERE c.customerID = %s", (session.get('user_id'),))
    cart = cursor.fetchall()
    cursor.close()

    # find cart total
    total = 0
    for item in cart:
        total += float(item["q"]) * float(item["pr"])


    print(url_for('product', product_id=1))
    return render_template("cart.html", cart=cart, total=round(total, 3))


@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product WHERE productID = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if request.method == "POST":
        if session.get('user_type') != 'customer':
            return redirect('/login')

        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cart WHERE customerID = %s AND productID = %s", (session.get('user_id'), product_id))
        cart_item = cursor.fetchone()
        cursor.close()

        if cart_item is None:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("INSERT INTO cart (customerID, productID, quantity) VALUES (%s, %s, %s)", (session.get('user_id'), product_id, 1))
            cnx.commit()
            cursor.close()
        else:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE customerID = %s AND productID = %s", (session.get('user_id'), product_id))
            cnx.commit()
            cursor.close()

        return redirect('/account/cart')

    return render_template("product.html", product=product)