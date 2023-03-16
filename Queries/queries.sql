-- Query-01: Place an order for a customer

-- Find out an available delivery agent
SELECT daID FROM delivery_agent WHERE availability = 1 ORDER BY daID ASC LIMIT 1;

-- Add the order to the table orders and assign the order to the selected delivery agent
INSERT INTO orders (customerID, daID, order_date)
VALUES (50, (SELECT daID FROM delivery_agent WHERE availability = 1 ORDER BY daID ASC LIMIT 1), '2021-04-01');

-- Add the ordered products in the table order_product
INSERT INTO order_product (orderID, productID, quantity)
SELECT MAX(o.orderID), c.productID, c.quantity
FROM orders o INNER JOIN cart c ON o.customerID = c.customerID
WHERE o.customerID = 50
GROUP BY c.productID;

-- Reduce the quantity of products ordered from table product
UPDATE product p INNER JOIN cart c ON p.productID = c.productID
SET p.quantity = p.quantity - c.quantity
WHERE c.customerID = 50;

-- Delete the products from the cart
DELETE FROM cart WHERE customerID = 50;

-- Update the wallet balance of the customer
UPDATE wallet w
INNER JOIN orders o ON w.customerID = o.customerID
SET w.balance = w.balance - (
    SELECT SUM(p.price * op.quantity)
    FROM product p, order_product op
    WHERE p.productID = op.productID AND op.orderID = o.orderID
);

-- Update the availability of the delivery agent
UPDATE delivery_agent
SET availability = 0
WHERE daID = (
    SELECT daID FROM orders WHERE customerID = 50 AND orderID = (
        SELECT MAX(orderID) FROM orders WHERE customerID = 50
    )
);

---------------------------------------------------------------------------------------------------------------------------------

-- Query-02: Get a list of all suppliers who have all their products with average rating above 3
SELECT s.supplierID, CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS name
FROM supplier s
WHERE (
    SELECT AVG(pr.rating) FROM product_review pr, product p
    WHERE p.productID = pr.productID AND p.supplierID = s.supplierID
    GROUP BY p.supplierID
) > 3;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-03: List the suppliers who do not sell any products
SELECT s.supplierID, CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS name
FROM supplier s
WHERE NOT EXISTS (
    SELECT * FROM product p
    WHERE p.supplierID = s.supplierID
);

---------------------------------------------------------------------------------------------------------------------------------

-- Query-04: Display the products that have average rating above or equal to 3.5 ordered by average rating
SELECT p.productID, p.name, AVG(pr.rating) AS avg_rating
FROM product_review pr, product p
WHERE p.productID = pr.productID
GROUP BY p.productID
HAVING AVG(pr.rating) >= 3.5
ORDER BY AVG(pr.rating) DESC;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-05: Display the top 40 delivery agents with the highest average rating
SELECT da.daID, CONCAT(da.first_name, ' ', da.middle_initial, ' ', da.last_name) AS name, AVG(dr.rating) AS avg_rating
FROM da_review dr, delivery_agent da
WHERE da.daID = dr.daID
GROUP BY da.daID
ORDER BY AVG(dr.rating) DESC
LIMIT 40;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-06: Show the undelivered orders of a delivery agent
SELECT orderID, customerID, daID, order_date, DATE_FORMAT(ADDDATE(order_date, INTERVAL 15 DAY), '%Y-%m-%d') AS ETA
FROM orders
WHERE daID = 1 AND delivery_date IS NULL;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-07: Display the entire record of a customer properly
SELECT
    customerID,
    CONCAT(first_name, ' ', middle_initial, ' ', last_name) AS name,
    CONCAT(apt_number, ', ', street_name, ', ', city, ', ', state, ' - ', zip, ', ', country) AS customer_address,
    age,
    ph.num as primary_phone_number,
    email
FROM
    customer,
    address,
    (SELECT num FROM phone_number, customer WHERE phone_number.phoneID = customer.phoneID AND customerID = 50 LIMIT 1) AS ph
WHERE customer.addressID = address.addressID
AND customer.customerID = 50;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-08: Show the top 15 customers who have spent the most money on their orders
SELECT customer.customerID,
COUNT(orders.orderID) AS total_orders,
SUM(product.price * order_product.quantity) AS total_spent
FROM customer
INNER JOIN orders ON customer.customerID = orders.customerID
INNER JOIN order_product ON orders.orderID = order_product.orderID
INNER JOIN product ON order_product.productID = product.productID
GROUP BY customer.customerID
ORDER BY total_spent DESC
LIMIT 15;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-09: View the order history of a customer
SELECT orders.orderID, orders.order_date, orders.delivery_date, product.name, order_product.quantity, product.price,
    (order_product.quantity * product.price) AS total_price,
    CASE
        WHEN (orders.delivery_date IS NULL) = True THEN 'Not Delivered'
        ELSE 'Delivered'
    END AS delivered
FROM orders
INNER JOIN order_product ON orders.orderID = order_product.orderID
INNER JOIN product ON order_product.productID = product.productID
WHERE orders.customerID = 1
ORDER BY orders.order_date;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-10: Find out the total price of an order
SELECT orderID, SUM(product.price * order_product.quantity) AS order_price
FROM order_product
INNER JOIN product ON order_product.productID = product.productID
WHERE order_product.orderID = 1;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-11: Show all underlivered orders with their ETA for a customer
SELECT orderID, order_date, DATE_FORMAT(ADDDATE(order_date, INTERVAL 15 DAY), "%Y-%m-%d") AS ETA
FROM orders
INNER JOIN customer ON orders.customerID = customer.customerID
WHERE customer.customerID = 1 AND orders.delivery_date IS NULL
ORDER BY order_date;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-12: Find out the total revenue and total quantity sold per product for a supplier (sales statistics)
SELECT
    product.name, SUM(order_product.quantity) AS total_quantity_sold,
    SUM(order_product.quantity * product.price) AS total_revenue
FROM product
INNER JOIN order_product ON product.productID = order_product.productID
INNER JOIN orders ON order_product.orderID = orders.orderID
WHERE product.supplierID = 1
GROUP BY product.name;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-13: Search through the product catalogue for products with similar names (using pattern matching)
SELECT name, AVG(rating)
FROM product
JOIN product_review ON product.productID = product_review.productID
WHERE name LIKE 'LED %'
GROUP BY name;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-14: Add a product to a customer's cart
INSERT INTO cart (customerID, productID, quantity) VALUES (50, 1, 1);

---------------------------------------------------------------------------------------------------------------------------------

-- Query-15: Add a new phone number into the table for a customer
INSERT INTO phone_number VALUES
((SELECT phoneID FROM customer WHERE customerID = 50), '1234567890');

---------------------------------------------------------------------------------------------------------------------------------

-- Query-16: Add more quantity of products for an existing product
UPDATE product SET quantity = quantity + 100 WHERE productID = 1;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-17: Update the address of a customer
UPDATE address SET
    apt_number = '100',
    street_name = 'Thomspon St.',
    city = 'Albany',
    state = 'New York',
    zip = '12207',
    country = 'United States'
WHERE addressID = (SELECT addressID FROM customer WHERE customerID = 1);

---------------------------------------------------------------------------------------------------------------------------------

-- Query-18: Delete a product from a customer's cart
DELETE FROM cart WHERE customerID = 99 AND productID = 14;

---------------------------------------------------------------------------------------------------------------------------------