CREATE DATABASE IF NOT EXISTS EBMS;
USE EBMS;

CREATE TABLE address (
    addressID INT NOT NULL AUTO_INCREMENT,
    street_name VARCHAR(255) NOT NULL,
    apt_number VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    zip INT NOT NULL,
    country VARCHAR(255) NOT NULL,         -- added country
    PRIMARY KEY (addressID)
)

-- ENTITY TABLES

CREATE TABLE admin (
    adminID INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,        -- renamed all fields called hashed_password to password
    PRIMARY KEY (adminID)
);

CREATE TABLE supplier (
    supplierID INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    middle_initial VARCHAR(10),
    last_name VARCHAR(255) NOT NULL,
    addressID INT NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (supplierID)
    FOREIGN KEY (addressID) REFERENCES address(addressID)
);

CREATE TABLE customer (
    customerID INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    middle_initial VARCHAR(10),
    last_name VARCHAR(255) NOT NULL,
    addressID INT NOT NULL,
    age INT NOT NULL,
    password VARCHAR(255) NOT NULL,
    phoneID INT NOT NULL,
    UNIQUE (phoneID)
    PRIMARY KEY (customerID)
    FOREIGN KEY (addressID) REFERENCES address(addressID)
);

CREATE TABLE delivery_agent (
    daID INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    middle_initial VARCHAR(10),
    last_name VARCHAR(255) NOT NULL,
    avalability BOOLEAN NOT NULL,
    phoneID INT NOT NULL,
    UNIQUE (phoneID)
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (daID)
);

CREATE TABLE phone_number (
    phoneID INT NOT NULL,
    phone_number CHAR(15) NOT NULL,
    FOREIGN KEY (phoneID) REFERENCES customer(phoneID)
    FOREIGN KEY (phoneID) REFERENCES delivery_agent(phoneID)
);

CREATE TABLE product (
    productID INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    supplierID INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,               -- added quantity
    PRIMARY KEY (productID, supplierID)
    FOREIGN KEY (supplierID) REFERENCES supplier(supplierID)
);

CREATE TABLE description (
    productID INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    PRIMARY KEY (productID)
    FOREIGN KEY (productID) REFERENCES product(productID)
);

CREATE TABLE order (
    orderID INT NOT NULL AUTO_INCREMENT,
    customerID INT NOT NULL,
    daID INT NOT NULL,
    order_date DATE NOT NULL,    -- added order_date
    delivery_date DATE,          -- added delivery_date
    ETA DATE NOT NULL,
    status BOOLEAN NOT NULL,
    PRIMARY KEY (orderID)
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
    FOREIGN KEY (daID) REFERENCES delivery_agent(daID)
);

CREATE TABLE wallet (
    customerID INT NOT NULL,
    balance DECIMAL(10,2) NOT NULL,
    upiID VARCHAR(255) NOT NULL,
    PRIMARY KEY (customerID)
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
);

-- removed reviewID
CREATE TABLE product_review (
    customerID INT NOT NULL,
    productID INT NOT NULL,
    supplierID INT NOT NULL,
    rating INT NOT NULL,
    content VARCHAR(255) NOT NULL,
    review_date DATE NOT NULL,
    PRIMARY KEY (customerID, productID, supplierID)
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
    FOREIGN KEY (productID) REFERENCES product(productID)
    FOREIGN KEY (supplierID) REFERENCES product(supplierID)
);

-- removed reviewID
CREATE TABLE da_review (
    customerID INT NOT NULL,
    daID INT NOT NULL,
    rating INT NOT NULL,
    content VARCHAR(255) NOT NULL,
    review_date DATE NOT NULL,
    PRIMARY KEY (customerID, daID)
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
    FOREIGN KEY (daID) REFERENCES delivery_agent(daID)
);

-- RELATIONSHIP TABLES

CREATE TABLE cart (
    customerID INT NOT NULL,
    productID INT NOT NULL,
    supplierID INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (customerID, productID, supplierID)
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
    FOREIGN KEY (productID) REFERENCES product(productID)
    FOREIGN KEY (supplierID) REFERENCES product(supplierID)
);

-- renamed "consists_of" relationship to "order_product"
CREATE TABLE order_product (
    orderID INT NOT NULL,
    productID INT NOT NULL,
    supplierID INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (orderID, productID, supplierID)
    FOREIGN KEY (orderID) REFERENCES order(orderID)
    FOREIGN KEY (productID) REFERENCES product(productID)
    FOREIGN KEY (supplierID) REFERENCES product(supplierID)
);

CREATE TABLE sold (
    supplierID INT NOT NULL,
    productID INT NOT NULL,
    quantity INT NOT NULL,
    sale_date DATE NOT NULL,
    PRIMARY KEY (productID, supplierID)
    FOREIGN KEY (productID) REFERENCES product(productID)
    FOREIGN KEY (supplierID) REFERENCES product(supplierID)
);

-- INDICES
-- TO DO LATER