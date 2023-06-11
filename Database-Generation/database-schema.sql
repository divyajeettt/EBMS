CREATE DATABASE IF NOT EXISTS EBMS;
USE EBMS;

-- UTILITIY TABLES

CREATE TABLE IF NOT EXISTS address (
    addressID INT NOT NULL AUTO_INCREMENT,
    street_name VARCHAR(255) NOT NULL,
    apt_number VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    zip INT NOT NULL,
    country VARCHAR(255) NOT NULL,
    PRIMARY KEY (addressID)
);

CREATE TABLE IF NOT EXISTS phone_number (
    phoneID INT NOT NULL,
    num CHAR(15) NOT NULL
);

-- ENTITY TABLES

CREATE TABLE IF NOT EXISTS admin (
    adminID INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL,
    PRIMARY KEY (adminID)
);

CREATE TABLE IF NOT EXISTS supplier (
    supplierID INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    middle_initial VARCHAR(10),
    last_name VARCHAR(255),
    addressID INT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL,
    PRIMARY KEY (supplierID),
    FOREIGN KEY (addressID) REFERENCES address(addressID)
);

CREATE TABLE IF NOT EXISTS customer (
    customerID INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    middle_initial VARCHAR(10),
    last_name VARCHAR(255),
    addressID INT NOT NULL,
    age INT NOT NULL,
    phoneID INT UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL,
    CHECK (age >= 18 AND age <= 120),
    PRIMARY KEY (customerID),
    FOREIGN KEY (addressID) REFERENCES address(addressID)
);

CREATE TABLE IF NOT EXISTS delivery_agent (
    daID INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    middle_initial VARCHAR(10),
    last_name VARCHAR(255),
    availability BOOLEAN NOT NULL DEFAULT TRUE,
    phoneID INT UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL,
    PRIMARY KEY (daID)
);

CREATE TABLE IF NOT EXISTS product (
    productID INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    supplierID INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    product_description TEXT NOT NULL,
    CHECK (price > 0.00),
    CHECK (quantity >= 0),
    PRIMARY KEY (productID),
    FOREIGN KEY (supplierID) REFERENCES supplier(supplierID)
);

CREATE TABLE IF NOT EXISTS orders (
    orderID INT NOT NULL AUTO_INCREMENT,
    customerID INT NOT NULL,
    daID INT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE,
    CHECK (delivery_date >= order_date),
    PRIMARY KEY (orderID),
    FOREIGN KEY (customerID) REFERENCES customer(customerID),
    FOREIGN KEY (daID) REFERENCES delivery_agent(daID)
);

CREATE TABLE IF NOT EXISTS wallet (
    customerID INT NOT NULL,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    upiID VARCHAR(255),
    CHECK (balance >= 0.00),
    PRIMARY KEY (customerID),
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
);

CREATE TABLE IF NOT EXISTS product_review (
    customerID INT NOT NULL,
    productID INT NOT NULL,
    rating INT NOT NULL,
    content TEXT,
    review_date DATE NOT NULL,
    CHECK (rating >= 1 AND rating <= 5),
    PRIMARY KEY (customerID, productID),
    FOREIGN KEY (customerID) REFERENCES customer(customerID),
    FOREIGN KEY (productID) REFERENCES product(productID)
);

CREATE TABLE IF NOT EXISTS da_review (
    customerID INT NOT NULL,
    daID INT NOT NULL,
    rating INT NOT NULL,
    content TEXT,
    review_date DATE NOT NULL,
    CHECK (rating >= 1 AND rating <= 5),
    PRIMARY KEY (customerID, daID),
    FOREIGN KEY (customerID) REFERENCES customer(customerID),
    FOREIGN KEY (daID) REFERENCES delivery_agent(daID)
);

-- RELATIONSHIP TABLES

CREATE TABLE IF NOT EXISTS cart (
    customerID INT NOT NULL,
    productID INT NOT NULL,
    quantity INT NOT NULL,
    CHECK (quantity >= 1),
    PRIMARY KEY (customerID, productID),
    FOREIGN KEY (customerID) REFERENCES customer(customerID),
    FOREIGN KEY (productID) REFERENCES product(productID)
);

CREATE TABLE IF NOT EXISTS order_product (
    orderID INT NOT NULL,
    productID INT NOT NULL,
    quantity INT NOT NULL,
    CHECK (quantity >= 1),
    PRIMARY KEY (orderID, productID),
    FOREIGN KEY (orderID) REFERENCES orders(orderID),
    FOREIGN KEY (productID) REFERENCES product(productID)
);

-- INDICES

CREATE UNIQUE INDEX admin_login ON admin(username, pwd);
CREATE UNIQUE INDEX supplier_login ON supplier(email, pwd);
CREATE UNIQUE INDEX customer_login ON customer(email, pwd);
CREATE UNIQUE INDEX da_login ON delivery_agent(email, pwd);
CREATE INDEX da_avalability ON delivery_agent(avalability);
CREATE UNIQUE INDEX customer_id ON wallet(customerID);
CREATE INDEX phone_id ON phone_number(phoneID);
CREATE INDEX address_id ON address(addressID);
CREATE INDEX product_name ON product(name);
CREATE INDEX product_price ON product(price);
CREATE INDEX product_review_rating ON product_review(rating);
CREATE INDEX product_review ON product_review(productID);
CREATE INDEX da_review_rating ON da_review(rating);
CREATE INDEX da_review ON da_review(daID);
CREATE INDEX customer ON cart(customerID);
CREATE INDEX order_num ON order_product(orderID);
CREATE INDEX sale_stats ON order_product(productID);