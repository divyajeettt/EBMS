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


@app.route("/catalogue")
def search():
    search = request.args.get("q")
    if search is None:
        query = """
            SELECT p.productID, p.name, p.price, AVG(pr.rating) AS avg_rating, p.quantity
            FROM product p
            LEFT JOIN product_review pr ON p.productID = pr.productID
            GROUP BY p.productID
            ORDER BY p.name ASC
        """
    else:
        query = f"""
            SELECT p.productID, p.name, p.price, AVG(pr.rating) AS avg_rating, p.quantity
            FROM product p
            LEFT JOIN product_review pr ON p.productID = pr.productID
            WHERE p.name LIKE '%{search}%'
            GROUP BY p.productID
            ORDER BY p.name ASC
        """

    with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        results = list(cursor.fetchall())

    return render_template("catalogue.html", rows=results)



@app.route('/login', methods=['GET', 'POST'])
def login():
    # TODO check if the user is a customer or supplier
    session.clear()

    if request.method == 'POST':
        if not request.form.get('username'):
            return render_template('login.html', error='Please enter your email')
        elif not request.form.get('password'):
            return render_template('login.html', error='Please enter your password')

        with cnx.cursor(dictionary=True) as cursor:
            if request.form['LoginRadio'] == 'customer':
                cursor.execute("SELECT customerID, first_name, email, pwd FROM customer WHERE email = %s", (request.form.get('username'),))
            elif request.form['LoginRadio'] == 'supplier':
                cursor.execute("SELECT supplierID, first_name, email, pwd FROM supplier WHERE email = %s", (request.form.get('username'),))
            elif request.form['LoginRadio'] == 'delivery_agent':
                cursor.execute("SELECT daID, first_name, email, pwd FROM delivery_agent WHERE email = %s", (request.form.get('username'),))
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
        elif request.form['LoginRadio'] == 'delivery_agent':
            session['user_id'] = user['daID']
            session['user_type'] = 'delivery_agent'
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
    if session.get('user_type') != 'admin':
        return redirect('/adminlogin')

    context = {}
    with cnx.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT ROUND(COUNT(*), -1) AS customer_count FROM customer")
        context["customer_count"] = cursor.fetchone()["customer_count"]

        cursor.execute("SELECT ROUND(COUNT(*), -1) AS supplier_count FROM supplier")
        context["supplier_count"] = cursor.fetchone()["supplier_count"]

        cursor.execute("SELECT ROUND(COUNT(*), -1) AS da_count FROM delivery_agent")
        context["da_count"] = cursor.fetchone()["da_count"]

        cursor.execute("SELECT ROUND(COUNT(*), -1) AS order_count FROM orders")
        context["order_count"] = cursor.fetchone()["order_count"]

        cursor.execute("SELECT ROUND(COUNT(*), -1) AS product_count FROM order_product")
        context["product_count"] = cursor.fetchone()["product_count"]

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
        cursor.execute(f"SELECT ROUND(COUNT(*), -1) AS n FROM {table}")
        context["count"] = cursor.fetchone()["n"]

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

            cursor.execute("""
                SELECT
                    country, state,
                    COUNT(DISTINCT customer.customerID) AS customer_count,
                    AVG(product.price * order_product.quantity) AS avg_spent,
                    SUM(product.price * order_product.quantity) AS total_spent
                FROM customer
                JOIN orders ON customer.customerID = orders.customerID
                JOIN order_product ON orders.orderID = order_product.orderID
                JOIN product ON order_product.productID = product.productID
                JOIN address ON customer.addressID = address.addressID
                GROUP BY country, state WITH ROLLUP
                ORDER BY country ASC, total_spent DESC
            """)
            context["demographics"] = cursor.fetchall()

        elif page == "order":
            cursor.execute("""
                SELECT (delivery_date IS NULL) as status, COUNT(*) AS n
                FROM orders
                GROUP BY status
            """)
            context["order_status"] = cursor.fetchall()

            cursor.execute("""
                SELECT
                    YEAR(order_date) AS date_year,
                    QUARTER(order_date) AS date_quarter,
                    DATE_FORMAT(order_date, '%M') AS date_month,
                    COUNT(orders.orderID) AS order_count,
                    SUM(price * order_product.quantity) AS revenue
                FROM
                    orders
                    JOIN order_product ON orders.orderID = order_product.orderID
                    JOIN product ON order_product.productID = product.productID
                GROUP BY date_year, date_quarter, date_month WITH ROLLUP
                ORDER BY date_year DESC, date_month DESC
            """)
            context["order_trend"] = cursor.fetchall()

            cursor.execute("""
                SELECT
                    a.country,
                    COUNT(DISTINCT o.orderID) AS order_count,
                    SUM(op.quantity * p.price) AS revenue
                FROM orders o
                JOIN order_product op ON o.orderID = op.orderID
                JOIN product p ON op.productID = p.productID
                JOIN customer c ON o.customerID = c.customerID
                JOIN address a ON c.addressID = a.addressID
                GROUP BY a.country WITH ROLLUP
                ORDER BY revenue DESC
            """)
            context["country_trend"] = cursor.fetchall()

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

            cursor.execute("""
                SELECT
                    country, state,
                    COUNT(DISTINCT supplier.supplierID) AS supplier_count,
                    AVG(product.price * order_product.quantity) AS avg_earned,
                    SUM(product.price * order_product.quantity) AS total_earned
                FROM supplier
                JOIN orders ON supplier.supplierID IN (
                    SELECT supplierID FROM product WHERE productID IN (
                        SELECT productID FROM order_product WHERE orderID = orders.orderID
                    )
                )
                JOIN order_product ON orders.orderID = order_product.orderID
                JOIN product ON order_product.productID = product.productID
                JOIN address ON supplier.addressID = address.addressID
                GROUP BY country, state WITH ROLLUP
                ORDER BY country ASC, total_earned DESC
            """)
            context["demographics"] = cursor.fetchall()

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
    session.clear()
    return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        if session.get("user_type") == "delivery_agent":
            print("not delivering...", request.form.get("order_id"))
            if request.form.get("order_id"):
                print("Delivering...")
                with cnx.cursor() as cursor:
                    cursor.execute("UPDATE orders SET delivery_date = CURDATE() WHERE orderID = %s;", (request.form.get('order_id'),))
                    cnx.commit()
                return redirect("/account")

    if session.get("user_type") == "customer":
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"""
                SELECT
                    CONCAT(first_name, ' ', last_name) AS name,
                    age, email,
                    CONCAT(apt_number, ', ', street_name) AS hno, CONCAT(city, ' - ', zip) AS location,
                    state, country
                FROM customer, address
                WHERE customer.addressID = address.addressID AND customer.customerID = {session.get("user_id")}
            """)
            user = cursor.fetchone()

            cursor.execute(f"""
                SELECT num FROM phone_number
                WHERE phoneID = (SELECT phoneID FROM customer WHERE customerID = {session.get("user_id")})
            """)
            user["phone"] = cursor.fetchall()

            cursor.execute(f"""
                SELECT
                    orderID, order_date, CONCAT(first_name, ' ', last_name) AS name,
                    DATE_FORMAT(ADDDATE(order_date, INTERVAL 15 DAY), '%Y-%m-%d') AS ETA
                FROM orders
                JOIN delivery_agent ON orders.daID = delivery_agent.daID
                WHERE customerID = 3 AND delivery_date IS NULL
                ORDER BY order_date DESC
            """)
            active_orders = cursor.fetchall()

            cursor.execute(f"""
                SELECT orderID, order_date, delivery_date, CONCAT(first_name, ' ', last_name) AS name
                FROM orders
                JOIN delivery_agent ON orders.daID = delivery_agent.daID
                WHERE customerID = {session.get("user_id")} AND delivery_date IS NOT NULL
                ORDER BY order_date DESC
            """)
            past_orders = cursor.fetchall()

        return render_template("account/customer.html", user=user, orders=[active_orders, past_orders])

    elif session.get('user_type') == 'supplier':
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT * FROM supplier WHERE supplierID = {session.get('user_id')}")
            user = cursor.fetchone()

        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT * FROM product WHERE supplierID = {session.get('user_id')}")
            products = cursor.fetchall()

        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"""SELECT
                product.name as product_name, SUM(order_product.quantity) AS total_quantity_sold,
                SUM(order_product.quantity * product.price) AS total_revenue
                FROM product
                INNER JOIN order_product ON product.productID = order_product.productID
                INNER JOIN orders ON order_product.orderID = orders.orderID
                WHERE product.supplierID = {session.get("user_id")}
                GROUP BY product.name
            """)
            sales = cursor.fetchall()

        return render_template('account/supplier.html', user=user, products=products, sales=sales)

    elif session.get('user_type') == 'delivery_agent':
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT * FROM delivery_agent WHERE daID = {session.get('user_id')}")
            user = cursor.fetchone()

            cursor.execute(f"""
                SELECT
                    orderID, customerID, daID, order_date,
                    DATE_FORMAT(ADDDATE(order_date, INTERVAL 15 DAY), '%Y-%m-%d') AS ETA
                FROM orders
                WHERE daID = {session.get('user_id')} AND delivery_date IS NULL
            """)
            active_orders = cursor.fetchall()

            cursor.execute(f"SELECT * FROM orders WHERE daID = {session.get('user_id')} AND delivery_date IS NOT NULL")
            completed_orders = cursor.fetchall()

        return render_template("account/deliveryagent.html", user=user, active_orders=active_orders, completed_orders=completed_orders)

    elif session.get("user_type") == "admin":
        return redirect("/admin")

    else:
        return redirect("/login")


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
        if request.form.get("action") == "remove":
            with cnx.cursor() as cursor:
                cursor.execute(f"DELETE FROM cart WHERE customerID = {session.get('user_id')} AND productID = {request.form.get('pid')}")
                cnx.commit()
            return redirect("/account/cart")

        elif request.form.get("action") == "checkout":
            return redirect("/account/checkout")

        elif request.form.get("action") == "clear":
            with cnx.cursor() as cursor:
                cursor.execute(f"DELETE FROM cart WHERE customerID = {session.get('user_id')}")
                cnx.commit()
            return redirect("/account/cart")

    with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(f"""
            SELECT
                p.productID, p.name AS pname, CONCAT(s.first_name, ' ', s.last_name) AS sname,
                p.product_description, c.quantity, ROUND((p.price * c.quantity), 2) AS total
            FROM cart c
            JOIN product p ON c.productID = p.productID
            JOIN supplier s ON p.supplierID = s.supplierID
            WHERE c.customerID = {session.get("user_id")}
            ORDER BY sname ASC, p.name ASC, total DESC
        """)
        cart = cursor.fetchall()

        cursor.execute(f"""
            SELECT ROUND(SUM(c.quantity * p.price), 2) AS total
            FROM cart c
            JOIN product p on c.productID = p.productID
            WHERE c.customerID = {session.get("user_id")}
        """)
        total = cursor.fetchone()["total"]

    return render_template("cart.html", cart=cart, total=total)


@app.route("/account/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        with cnx.cursor() as cursor:
            cursor.execute("""
                SELECT daID FROM delivery_agent
                WHERE avalability = 1
                ORDER BY daID ASC LIMIT 1
            """)
            daID = cursor.fetchone()[0]

            cursor.execute(f"""
                INSERT INTO orders (customerID, daID, order_date)
                VALUES ({session.get("user_id")}, {daID}, CURDATE())
            """)
            cnx.commit()

            cursor.execute("SELECT LAST_INSERT_ID();")
            order_id = cursor.fetchone()[0]

            cursor.execute(f"""
                INSERT INTO order_product (orderID, productID, quantity)
                SELECT {order_id}, c.productID, c.quantity
                FROM orders o
                INNER JOIN cart c ON o.customerID = c.customerID
                WHERE o.customerID = {session.get("user_id")}
                GROUP BY c.productID""")
            cnx.commit()

            # UPDATE THE DELIVERY AGENT AVAILABILITY -- no need
            # cursor.execute("""UPDATE delivery_agent
            #                 SET avalability = 0
            #                 WHERE daID = (SELECT daID FROM orders WHERE orderID = %s);""", (order_id,))
            cnx.commit()

            # UPDATE PRODUCT QUANTITY
            cursor.execute(f"""
                UPDATE product p
                INNER JOIN cart c ON p.productID = c.productID
                SET p.quantity = p.quantity - c.quantity
                WHERE c.customerID = {session.get("user_id")}
            """)

            cursor.execute(f"DELETE FROM cart WHERE customerID = {session.get('user_id')}")
            cnx.commit()

        return redirect("/account/checkout")

    with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(f"""
            SELECT p.productID, p.name, c.quantity, p.price, ROUND((p.price * c.quantity), 2) AS total
            FROM cart c
            JOIN product p on c.productID = p.productID
            WHERE c.customerID = {session.get("user_id")}
        """)
        cart = cursor.fetchall()

        cursor.execute(f"""
            SELECT ROUND(SUM(c.quantity * p.price), 2) AS total
            FROM cart c
            JOIN product p on c.productID = p.productID
            WHERE c.customerID = {session.get("user_id")}
        """)
        total = cursor.fetchone()["total"]

        cursor.execute(f"""
            SELECT
                CONCAT(first_name, ' ', last_name) AS name,
                age, ph.num as phone, email,
                CONCAT(apt_number, ', ', street_name) AS hno, CONCAT(city, ' - ', zip) AS location,
                state, country
            FROM customer, address, (
                SELECT num FROM phone_number, customer
                WHERE phone_number.phoneID = customer.phoneID
                AND customerID = {session.get("user_id")}
                LIMIT 1
            ) AS ph
            WHERE customer.addressID = address.addressID AND customer.customerID = {session.get("user_id")}
        """)
        user = cursor.fetchone()

    return render_template("checkout.html", cart=cart, total=total, user=user)


@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    qty = request.args.get("qty")
    edit = request.args.get("edit")
    message = request.args.get("message")

    if request.method == "POST":
        if session.get("user_type") != "customer":
            return redirect("/login")

        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(f"""
                SELECT * FROM cart
                WHERE customerID = {session.get("user_id")} AND productID = {product_id}
            """)
            cart_item = cursor.fetchone()

            if cart_item is None:
                cursor.execute(f"INSERT INTO cart VALUES ({session.get('user_id')}, {product_id}, {qty})")
                dest = f"/product/{product_id}?message=Item+added+to+cart"

            elif edit:
                cursor.execute(f"""
                    UPDATE cart SET quantity = {qty}
                    WHERE customerID = {session.get("user_id")} AND productID = {product_id}
                """)
                dest = "/account/cart"

            else:
                cursor.execute(f"""
                    UPDATE cart SET quantity = quantity + {qty}
                    WHERE customerID = {session.get("user_id")} AND productID = {product_id}
                """)
                dest = f"/product/{product_id}?message=More+items+added+to+cart"

            cnx.commit()

        return redirect(dest)

    context = {}
    with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(f"SELECT * FROM product WHERE productID = {product_id}")
        product = context["product"] = cursor.fetchone()

        cursor.execute(f"""
            SELECT CONCAT(first_name, ' ', last_name) as name, rating, content, DATE_FORMAT(review_date, '%M %d, %Y') as date
            FROM customer
            INNER JOIN product_review ON customer.customerID = product_review.customerID
            WHERE productID = {product_id}
            ORDER BY review_date DESC
            LIMIT 6;
        """)
        context["reviews"] = cursor.fetchall()

        cursor.execute(f"""
            SELECT COUNT(*) AS reviews, ROUND(AVG(rating), 2) AS stars
            FROM product_review
            WHERE productID = {product_id}
        """)
        context["rating"] = cursor.fetchone()

        cursor.execute(f"""
            SELECT CONCAT(first_name, ' ', last_name) as name
            FROM supplier
            WHERE supplierID = {product["supplierID"]}
        """)
        context["supplier"] = cursor.fetchone()

        if session.get("user_type") == "customer":
            cursor.execute(f"SELECT quantity FROM cart WHERE customerID = {session.get('user_id')} AND productID = {product_id}")
            in_cart = cursor.fetchone()
            context["in_cart"] = in_cart["quantity"] if in_cart is not None else 0
        else:
            context["in_cart"] = 0

        cursor.execute(f"""
            SELECT product.productID, name, product_description, price, ROUND(AVG(rating), 2) as rating
            FROM product
            LEFT JOIN product_review ON product.productID = product_review.productID
            WHERE supplierID = {product["supplierID"]} AND product.productID != {product_id}
            GROUP BY product.productID
            ORDER BY RAND()
            LIMIT 3
        """)
        context["more"] = cursor.fetchall()

    return render_template("product.html", context=context, qty=qty, edit=edit, message=message)


# @app.route("/account/track/<int:order_id>", methods=["GET", "POST"])
# @login_required
# def track(order_id):
#     if session.get('user_type') == 'customer':
#         cursor = cnx.cursor(dictionary=True)
#         cursor.execute("SELECT o.orderID as i, o.order_date as o_d, o.delivery_date as d_d, o.daID as daID FROM orders o WHERE o.customerID = %s AND o.orderID = %s", (session.get('user_id'), order_id))
#         order = cursor.fetchone()
#         cursor.close()

#         return render_template("track.html", order=order)
#     else:
#         return redirect('/login')
