from flask import Flask, render_template
from dotenv import load_dotenv
import os

import mysql.connector

app = Flask(__name__)

load_dotenv(verbose=True)
# Set up database connection
cnx = mysql.connector.connect(
                                user=os.getenv('DATABASE_USER'),
                                host='localhost',
                                password=os.getenv('DATABASE_PASSWORD'),
                                database=os.getenv('DATABASE_NAME')
                             )



@app.route('/')
def index():
    return render_template('home.html')

# @app.route('/search', methods=['GET', 'POST'])
@app.route('/search')
def search():
    # if request.method == 'POST':
    #     search = request.form['search']
    #     cursor = cnx.cursor()
    #     cursor.execute("SELECT * FROM EBMS WHERE name LIKE %s", (search,))
    #     results = cursor.fetchall()
    #     return render_template('home.html', rows=results)
    # return render_template('home.html')

    cursor = cnx.cursor()

    # Execute a query
    query = 'SELECT * FROM product'
    cursor.execute(query)

    # Fetch the results
    # converting to list to fully exhaust the generator before closing the cursor
    results = list(cursor.fetchall())

    # Close the cursor and connection
    cursor.close()

    return render_template('search.html', rows=results)

