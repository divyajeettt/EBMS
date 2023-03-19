import os

# from cs50 import SQL



from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import time

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

secQues = "What is the name of your childhood best friend"


@app.route("/")
@login_required
def index():
    buysinfo = db.execute("SELECT * FROM buys WHERE id = :thisid ORDER BY symbol", thisid=session["user_id"])
    sellsinfo = db.execute("SELECT * FROM sells WHERE id = :thisid ORDER BY symbol", thisid=session["user_id"])
    userinfo = db.execute("SELECT * FROM users WHERE id = :thisid", thisid=session["user_id"])

    thebuyslist = []

    for row in buysinfo:
        thedict = lookup(row["symbol"])
        thebuyslist.append({"symbol" : row["symbol"], "name" : thedict["name"], "price" : thedict["price"],  "shares" : row["stocks"]})

    thesellslist = []

    for row in sellsinfo:
        thedict = lookup(row["symbol"])
        thesellslist.append({"symbol" : row["symbol"], "shares" : row["stocks"]})

    uniSyms = {}

    for ARecord in thebuyslist:
        if ARecord["symbol"] in uniSyms:
            uniSyms[ARecord["symbol"]] += ARecord["shares"]
            ARecord["shares"] = "na"
        else:
            uniSyms[ARecord["symbol"]] = ARecord["shares"]

    for BRecord in thesellslist:
        if BRecord["symbol"] in uniSyms:
            uniSyms[BRecord["symbol"]] += BRecord["shares"]

    gtotal = 0

    # for key in uniSyms:
    #     gtotal += uniSyms[key]*lookup(key)["price"]


    return render_template("index.html", thebuyslist=thebuyslist, thesellslist=thesellslist, length=len(thebuyslist), gtotal=gtotal, cash=userinfo[0]["cash"], uniSyms=uniSyms)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
         return render_template("buy.html")

    else:
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        # Ensure shares submitted
        elif not request.form.get("shares"):
            return apology("must provide shares", 403)

        try:
            if int(request.form.get("shares")) < 1:
                return apology("invalid number of shares", 403)

        except:
            return apology("invalid number of shares", 403)

        symbol = request.form.get("symbol").upper()

        if lookup(symbol) == None:
            return apology("invalid symbol", 400)

        else:
            shares = int(request.form.get("shares"))

            rows = db.execute("SELECT * FROM users WHERE id = :thisid", thisid=session["user_id"])

            cash = rows[0]["cash"]

            price = float(lookup(symbol)["price"])

            if cash < shares*price:
                return apology("can't afford", 400)

            else:
                db.execute("UPDATE users SET cash = :cash WHERE id = :thisid", cash = cash-shares*price, thisid = session["user_id"])

                db.execute("INSERT INTO buys VALUES (:thisid, :symbol, :bprice, :stocks, :time)",
                thisid = session["user_id"], symbol = symbol, bprice = price, stocks = shares, time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time())))

                return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    hist = db.execute("SELECT id, symbol, bprice as price, stocks, time FROM buys WHERE id = :thisid UNION SELECT id, symbol, sprice as price, stocks, time FROM sells WHERE id = :thisid ORDER BY time desc", thisid=session['user_id'])

    return render_template("history.html", hist=hist, length=len(hist))



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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
         return render_template("quote.html")

    else:
        symbol = request.form.get("symbol").upper()

        if lookup(symbol) == None:
            return apology("invalid symbol", 400)

        else:
            return render_template("quoted.html", name=lookup(symbol)["name"], price=lookup(symbol)["price"], symbol=symbol)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

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

        elif not request.form.get("re-password"):
            return apology("must enter password again", 403)

        elif request.form.get("password") != request.form.get("re-password"):
            return apology("passwords don't match", 400)

        password = request.form.get("password")

        for i in password:
            if i == ' ':
                return apology("password doesn't meet the requirements", 403)

        for i in password:
            if i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                break
        else:
            return apology("password doesn't meet the requirements", 403)

        for i in password:
            if i in '1234567890':
                break
        else:
            return apology("password doesn't meet the requirements", 403)

        for i in password:
            if (ord(i)>32 and ord(i)<48) or (ord(i)>57 and ord(i)<65) or (ord(i)>90 and ord(i)<97) or (ord(i)>122 and ord(i)<127):
                break
        else:
            return apology("password doesn't meet the requirements", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) == 1:
            return apology("username is taken", 403)

        # Query database for username
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :phash)" ,
                          username=request.form.get("username"), phash=generate_password_hash(request.form.get("password")))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        if not request.form.get("shares"):
            return apology("must provide shares", 403)

        try:
            if int(request.form.get("shares")) < 1:
                return apology("invalid number of shares", 403)

        except:
            return apology("invalid number of shares", 403)

        sell_symbol = request.form.get("symbol").upper()

        sell_shares = int(request.form.get("shares"))


        buysinfo = db.execute("SELECT * FROM buys WHERE id = :thisid ORDER BY symbol", thisid=session["user_id"])
        sellsinfo = db.execute("SELECT * FROM sells WHERE id = :thisid ORDER BY symbol", thisid=session["user_id"])
        userinfo = db.execute("SELECT * FROM users WHERE id = :thisid", thisid=session["user_id"])

        thebuyslist = []

        for row in buysinfo:
            thebuyslist.append({"symbol" : row["symbol"], "shares" : row["stocks"]})

        thesellslist = []

        for row in sellsinfo:
            thesellslist.append({"symbol" : row["symbol"], "shares" : row["stocks"]})

        uniSyms = {}

        for ARecord in thebuyslist:
            if ARecord["symbol"] in uniSyms:
                uniSyms[ARecord["symbol"]] += ARecord["shares"]
            else:
                uniSyms[ARecord["symbol"]] = ARecord["shares"]

        for BRecord in thesellslist:
            if BRecord["symbol"] in uniSyms:
                uniSyms[BRecord["symbol"]] += BRecord["shares"]

        for syms in uniSyms:
            if syms.upper() != sell_symbol.upper():
                continue
            if sell_shares > uniSyms[syms]:
                return apology("too many shares to sell", 400)

        cash = userinfo[0]["cash"]

        price = int(lookup(sell_symbol)["price"])

        db.execute("UPDATE users SET cash = :cash WHERE id = :thisid", cash = cash+sell_shares*price, thisid = session["user_id"])
        db.execute("INSERT INTO sells VALUES (:thisid, :symbol, :sprice, :stocks, :time)",
        thisid = session["user_id"], symbol = sell_symbol, sprice = price, stocks = -1*sell_shares, time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time())))

        return redirect("/")

    else:
        buysinfo = db.execute("SELECT * FROM buys WHERE id = :thisid ORDER BY symbol", thisid=session["user_id"])
        sellsinfo = db.execute("SELECT * FROM sells WHERE id = :thisid ORDER BY symbol", thisid=session["user_id"])
        userinfo = db.execute("SELECT * FROM users WHERE id = :thisid", thisid=session["user_id"])

        thebuyslist = []

        for row in buysinfo:
            thebuyslist.append({"symbol" : row["symbol"], "shares" : row["stocks"]})

        thesellslist = []

        for row in sellsinfo:
            thesellslist.append({"symbol" : row["symbol"], "shares" : row["stocks"]})

        uniSyms = {}

        for ARecord in thebuyslist:
            if ARecord["symbol"] in uniSyms:
                uniSyms[ARecord["symbol"]] += ARecord["shares"]
            else:
                uniSyms[ARecord["symbol"]] = ARecord["shares"]

        for BRecord in thesellslist:
            if BRecord["symbol"] in uniSyms:
                uniSyms[BRecord["symbol"]] += BRecord["shares"]

        return render_template("sell.html", uniSyms=uniSyms)






def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
