CREATE TABLE admin (
    adminID INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (adminID)
);

CREATE TABLE supplier (
    supplierID INT NOT NULL AUTO_INCREMENT,
    /* name VARCHAR(255) NOT NULL, */
    /* address VARCHAR(255) NOT NULL, */
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (supplierID)
);

CREATE TABLE customer (
    customerID INT NOT NULL AUTO_INCREMENT,
    /* name VARCHAR(255) NOT NULL, */
    /* address VARCHAR(255) NOT NULL, */
    age INT NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number CHAR(15) NOT NULL,
    PRIMARY KEY (customerID)
);

CREATE TABLE delivery_agent (
    daID INT NOT NULL AUTO_INCREMENT,
    /* name VARCHAR(255) NOT NULL, */
    avalability BOOLEAN NOT NULL,
    phone_number CHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (daID)
);

CREATE TABLE product (
    productID INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    supplierID INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
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
    /* order_date DATE NOT NULL, */
    /* delivery_date DATE NOT NULL, */
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

CREATE TABLE product_review (
    reviewID INT NOT NULL AUTO_INCREMENT,
    customerID INT NOT NULL,
    productID INT NOT NULL,
    supplierID INT NOT NULL,
    stars INT NOT NULL,
    content VARCHAR(255) NOT NULL,
    review_date DATE NOT NULL,
    PRIMARY KEY (reviewID)
    /* PRIMARY KEY (productID, customerID) */
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
    FOREIGN KEY (productID) REFERENCES product(productID)
    FOREIGN KEY (supplierID) REFERENCES product(supplierID)
);

CREATE TABLE da_review (
    reviewID INT NOT NULL AUTO_INCREMENT,
    customerID INT NOT NULL,
    daID INT NOT NULL,
    stars INT NOT NULL,
    content VARCHAR(255) NOT NULL,
    review_date DATE NOT NULL,
    PRIMARY KEY (reviewID)
    /* PRIMARY KEY (daID, customerID) */
    FOREIGN KEY (customerID) REFERENCES customer(customerID)
    FOREIGN KEY (daID) REFERENCES delivery_agent(daID)
);

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

/* consist_of relation */
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