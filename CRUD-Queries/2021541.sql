-- CREATE

-- insert a new phone number for customer=1;
INSERT INTO phone_number VALUES
((SELECT phoneID FROM customer WHERE customerID = 1), '1234567890');
-- auxiliary query for checking insertion
SELECT * FROM phone_number WHERE phoneID = (SELECT phoneID FROM customer WHERE customerID = 1);


-- add a product to the cart of a customer with customerID = 50;
INSERT INTO cart (customerID, productID, quantity) VALUES (50, 1, 1);
-- auxiliary query for checking insertion
SELECT * FROM cart WHERE customerID=50;


-- when an order is placed, the product should be removed from the cart, and the quantity should be reduced from the product table;
INSERT INTO orders (customerID, daID, order_date) VALUES (1, 1, '2021-04-01');
INSERT INTO order_product (orderID, productID, quantity) 
    SELECT MAX(o.orderID), c.productID, c.quantity
    FROM orders AS o INNER JOIN cart AS c ON o.customerID=c.customerID
    WHERE o.customerID = 1
    GROUP BY c.productID;
-- reduce the quantity of the product in the product table by the quantity in the cart, products will be iterated through programatically;
UPDATE product p SET quantity = quantity - 15 WHERE productID=82;
DELETE FROM cart WHERE customerID = 1;
UPDATE delivery_agent SET avalability = 0 WHERE daID = 1;
-- auxiliary query for checking order placement
SELECT * FROM orders WHERE customerID=1;
SELECT * FROM order_product WHERE orderID=1001;
SELECT * FROM product WHERE productID=82;
SELECT * FROM cart WHERE customerID=1;
SELECT * FROM delivery_agent WHERE daID=1;






-- READ


-- show all suppliers who have all their products with rating above (or equal to) 4;
SELECT s.supplierID, CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS name FROM supplier s
WHERE NOT EXISTS ( (
        SELECT avg(rating) FROM product_review, product WHERE product_review.productID = product.productID AND product.supplierID = s.supplierID
    ) EXCEPT (
        SELECT avg(rating) from product_review GROUP BY productID HAVING avg(rating) >= 4
    )
);


-- show all suppliers that do not sell any products;
SELECT s.supplierID, CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS name FROM supplier s
WHERE NOT EXISTS (SELECT * FROM product WHERE product.supplierID = s.supplierID);


-- show all products that have the average rating above (or equal to) 3.5, ordered by the average rating;
SELECT p.productID, p.name, AVG(pr.rating) FROM product_review pr, product p
WHERE p.productID = pr.productID
GROUP BY p.productID HAVING AVG(pr.rating) >= 3.5
ORDER BY AVG(pr.rating) DESC;

-- show the top 40 delivery agents with the highest average rating;
SELECT da.daID, CONCAT(da.first_name, ' ', da.middle_initial, ' ', da.last_name) AS name, AVG(dr.rating)
FROM da_review dr, delivery_agent da WHERE da.daID = dr.daID GROUP BY da.daID ORDER BY AVG(dr.rating) DESC LIMIT 40;


-- show the entire record of a customer with customerID = 25;
SELECT 
    customerID,
    CONCAT(first_name, ' ', middle_initial, ' ', last_name) AS name,
    CONCAT(apt_number, ', ', street_name, ', ', city, ', ', state, ' - ', zip, ', ',  country) AS customer_address,
    age,
    ph.num AS first_phone_num,
    email
FROM
    customer,
    address,
    (SELECT num FROM phone_number, customer WHERE phone_number.phoneID = customer.phoneID AND customerID = 25 LIMIT 1) AS ph
WHERE customer.addressID = address.addressID
AND customer.customerID = 25;


-- show the orders of a delivery agent where delivery_date is null;
SELECT orderID, customerID, daID, order_date, DATE_FORMAT(ADDDATE(order_date, INTERVAL 15 DAY), "%Y-%m-%d") AS ETA
FROM orders WHERE daID = 1 AND delivery_date IS NULL;





-- select top 15 customers who have spent the most money on products;
SELECT customer.customerID, COUNT(orders.orderID) as 'Total Orders', SUM(product.price * order_product.quantity) as 'Total Spent'
FROM customer
INNER JOIN orders ON customer.customerID = orders.customerID
INNER JOIN order_product ON orders.orderID = order_product.orderID
INNER JOIN product ON order_product.productID = product.productID
GROUP BY customer.customerID
ORDER BY SUM(product.price * order_product.quantity) DESC
LIMIT 15;

-- show the order history of a customer with customerID = 1;
SELECT
    orders.orderID, orders.order_date, orders.delivery_date, product.name, order_product.quantity, product.price,
    (order_product.quantity * product.price) AS total_price,
    CASE
        WHEN (orders.delivery_date IS NULL) = 'True' THEN 'Delivered'
        ELSE 'Not Delivered'
    END AS delivered
FROM orders
INNER JOIN order_product ON orders.orderID = order_product.orderID
INNER JOIN product ON order_product.productID = product.productID
WHERE orders.customerID = 1
ORDER BY orders.order_date;


-- show the total price of an order with orderID = 1;
SELECT orderID, SUM(price * order_product.quantity) AS 'Order Price'
FROM order_product
INNER JOIN product ON product.productID = order_product.productID
WHERE order_product.orderID = 1;


-- show ALL undelivered orders with their ETA for a customer = 1
SELECT orderID, order_date, DATE_FORMAT(ADDDATE(order_date, INTERVAL 15 DAY), "%Y-%m-%d") AS 'ETA' 
FROM orders
INNER JOIN customer ON orders.customerID = customer.customerID
WHERE customer.customerID = 1 AND orders.delivery_date IS NULL
ORDER BY order_date;


-- show the total revenue and total quantity sold per product of that supplier
SELECT product.name, SUM(order_product.quantity) AS total_quantity_sold, SUM(order_product.quantity * product.price) AS total_revenue
FROM product
INNER JOIN order_product ON product.productID = order_product.productID
INNER JOIN orders ON order_product.orderID = orders.orderID
WHERE product.supplierID = 1
GROUP BY product.name;


-- search for the names of products using pattern matching
SELECT name, AVG(rating)
FROM product
JOIN product_review ON product.productID = product_review.productID
WHERE name LIKE 'LED %'
GROUP BY name;






-- UPDATE

-- update the address of customer with customerID = 1
UPDATE address SET
    apt_number = '100',
    street_name = 'Thompson St.',
    city = 'Albany',
    state = 'New York',
    zip = '12207',
    country = 'United States'
WHERE addressID = (SELECT addressID FROM customer WHERE customerID = 1);


-- increase quantity by 100 of product with productID = 1
UPDATE product SET quantity = quantity + 100 WHERE productID = 1;






-- DELETE

-- delete a product from the cart
DELETE FROM cart WHERE productID = 14 AND customerID = 99;
