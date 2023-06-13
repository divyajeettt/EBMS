# EBMS

## About EBMS

ElectroBase Management System is a data management system for an online electronics store. It is a full-stack project developed as the Final Project for the course **[CSE202: *Fundamentals of Database Management System*](http://techtree.iiitd.edu.in/viewDescription/filename?=CSE202)**. The final report meets the requirements and deliverables of the project.

EBMS aims to solve the problem of managing an online electronics store by bringing together all the stakeholders, namely Administrators, Customers, Suppliers, and Delivery Agents on a common platform. It serves to provide a complete back-end solution for the store, including the management of its inventory of products, orders by customers, deliverues by suppliers and delivery agents.

## Run

Clone the repository on your device and navigate to the folder. The project requires a Python Environment and MySQL Server installed on your device. Run the following command to install the dependencies:

```bash
pip install -r requirements.txt
```

Activate the virtual environment using the command:

```bash
python3 -m venv ./front-end/flask_venv
source flask_venv/bin/activate
```

Add the details of the MySQL server and database in the file `./front-end/app/.env` using the format given in `./front-end/app/.sample_env`.

Run the following command to start the server:

```bash
python3 ./front-end/run.py
```

## Future Plans

- Enable functionality of the "Edit" button on user profiles.
- Enable functionality of the search bars on Admin Dashboard.
- Update the product catalogue to show cards (like the ones in cart) instead of a table.
- Enable the supplier to view the number of orders for each of their product, and move the features to a supplier dashboard.
- Enable the supplier to download the sales statistics.
- The project currently displays all prices, order costs, etc. in INR. A forex API may be used to convert the prices to USD, EUR, etc. based on the user's prefernce. This preference may be decided at the time of registration and stored in the database.
- Addition of graphs and charts to display trends along with tabular data.
- Addition of storage of images for products and user profiles in the database.
- Add robustness against SQL injection attacks.
- Addition of a dark mode.
- An ML model may be used to generate the "Hot-Picks for You" category on a user's home page.
- Improvement of UI/UX of the website.
