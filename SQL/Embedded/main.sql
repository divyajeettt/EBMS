-- Query-01: Display the product catalogue

-- Show the entire catalogue
SELECT p.productID, p.name, p.price, AVG(pr.rating) AS avg_rating, p.quantity
FROM product p
LEFT JOIN product_review pr ON p.productID = pr.productID
GROUP BY p.productID
ORDER BY p.name ASC;

-- Show the catalogue using searching for a product name
SELECT p.productID, p.name, p.price, AVG(pr.rating) AS avg_rating, p.quantity
FROM product p
LEFT JOIN product_review pr ON p.productID = pr.productID
WHERE p.name LIKE '%{search}%'
GROUP BY p.productID
ORDER BY p.name ASC;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-02: Get the login credentials

-- Query for customer
SELECT customerID, first_name, email, pwd FROM customer WHERE email = %s;

-- Query for supplier
SELECT supplierID, first_name, email, pwd FROM supplier WHERE email = %s;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-03: Get an overview of statistics for the admin

-- Query for the number of customers
SELECT COUNT(*) AS customer_count FROM customer;

-- Query for the number of suppliers
SELECT COUNT(*) AS supplier_count FROM supplier;

-- Query for the number of delivery agents
SELECT COUNT(*) AS da_count FROM delivery_agent;

-- Query for the number of orders
SELECT COUNT(*) AS order_count FROM orders;

-- Query for the number of products ordered
SELECT COUNT(*) AS product_count FROM order_product;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-04: Get the top-10 customers who have spent the most money on their orders
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
LIMIT 10;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-05: Get the number of delivered and undelivered orders
SELECT (delivery_date IS NULL) as status, COUNT(*) AS n FROM orders GROUP BY status;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-06: Get the top-10 inactive customers who have the least number of orders
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
LIMIT 10;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-07: Get the top-10 best-selling (most ordered) products
SELECT p.productID, p.name, p.price, SUM(op.quantity) AS quantity
FROM order_product op, product p
WHERE p.productID = op.productID
GROUP BY p.productID
ORDER BY quantity DESC
LIMIT 10;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-08: Get the top-10 highest rated products (based on average rating)
SELECT p.productID, p.name, p.price, AVG(pr.rating) AS avg_rating
FROM product_review pr, product p
WHERE p.productID = pr.productID
GROUP BY p.productID
HAVING avg_rating >= 3.5
ORDER BY avg_rating DESC
LIMIT 10;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-09: Get the first 10 inactive suppliers, i.e. those who have not supplied any products
SELECT
    s.supplierID,
    CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS name,
    email
FROM supplier s
WHERE NOT EXISTS (SELECT * FROM product p WHERE p.supplierID = s.supplierID)
LIMIT 10;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-10: Get the top-10 suppliers with the highest average rating
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
LIMIT 10;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-11: Get the top-10 delivery agents with the highest average rating
SELECT
    da.daID,
    CONCAT(da.first_name, ' ', da.middle_initial, ' ', da.last_name) AS name,
    email,
    AVG(dr.rating) AS avg_rating
FROM da_review dr, delivery_agent da
WHERE da.daID = dr.daID
GROUP BY da.daID
ORDER BY avg_rating DESC
LIMIT 10;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-12: Get the first 10 most active delivery agents, i.e. those who delivered the most number of orders
SELECT
    da.daID,
    CONCAT(da.first_name, ' ', da.middle_initial, ' ', da.last_name) AS name,
    email,
    COUNT(o.orderID) AS total_orders
FROM delivery_agent da
LEFT JOIN orders o ON da.daID = o.daID
GROUP BY da.daID
ORDER BY total_orders DESC
LIMIT 10;