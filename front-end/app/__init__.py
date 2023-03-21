from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

import mysql.connector

app = Flask(__name__)

load_dotenv(verbose=True)
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

    return render_template("search.html", rows=results)
