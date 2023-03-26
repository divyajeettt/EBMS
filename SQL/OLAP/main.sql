-- Query-01: Find out the trends in the number of orders on a monthly, quarterly, and yearly basis
SELECT
    YEAR(order_date) AS date_year,
    QUARTER(order_date) AS date_quarter,
    MONTH(order_date) AS date_month,
    COUNT(orders.orderID) AS order_count,
    SUM(price * order_product.quantity) AS revenue
FROM
    orders
    JOIN order_product ON orders.orderID = order_product.orderID
    JOIN product ON order_product.productID = product.productID
GROUP BY date_year, date_quarter, date_month WITH ROLLUP
ORDER BY date_year DESC, date_month DESC;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-02: Find out the country-wise trends in the number of orders and revenue
SELECT
    a.country,
    COUNT(DISTINCT o.orderID) AS order_count,
    SUM(op.quantity * p.price) AS revenue
FROM orders o
JOIN order_product op ON o.orderID = op.orderID
JOIN product p ON op.productID = p.productID
JOIN customer c ON o.customerID = c.customerID
JOIN address a ON c.addressID = a.addressID
GROUP BY a.country WITH ROLLUP
ORDER BY revenue DESC;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-03: retrieve the demographics of customer activity
SELECT
    country, state,
    COUNT(DISTINCT customer.customerID) AS customer_count,
    AVG(product.price * order_product.quantity) AS avg_spent,
    SUM(product.price * order_product.quantity) AS total_spent
FROM customer
JOIN orders ON customer.customerID = orders.customerID
JOIN order_product ON orders.orderID = order_product.orderID
JOIN product ON order_product.productID = product.productID
JOIN address ON customer.addressID = address.addressID
GROUP BY country, state WITH ROLLUP
ORDER BY country ASC, total_spent DESC;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-04: retrieve the demographics of supplier activity
SELECT
    country, state,
    COUNT(DISTINCT supplier.supplierID) AS supplier_count,
    AVG(product.price * order_product.quantity) AS avg_earned,
    SUM(product.price * order_product.quantity) AS total_earned
FROM supplier
JOIN orders ON supplier.supplierID IN (
    SELECT supplierID FROM product WHERE productID IN (
        SELECT productID FROM order_product WHERE orderID = orders.orderID
    )
)
JOIN order_product ON orders.orderID = order_product.orderID
JOIN product ON order_product.productID = product.productID
JOIN address ON supplier.addressID = address.addressID
GROUP BY country, state WITH ROLLUP
ORDER BY country ASC, total_earned DESC;

---------------------------------------------------------------------------------------------------------------------------------

-- Query-05: Find out a supplier's statistics by date and region
SELECT
    YEAR(order_date) AS year,
    MONTH(order_date) AS month,
    country,
    COUNT(DISTINCT o.orderID) AS total_quantity,
    SUM(op.quantity * p.price) AS total_sales
FROM orders o
JOIN order_product op ON o.orderID = op.orderID
JOIN product p ON op.productID = p.productID
JOIN customer c ON o.customerID = c.customerID
JOIN address a ON c.addressID = a.addressID
JOIN supplier s ON p.supplierID = s.supplierID
WHERE s.supplierID = {s_id}
GROUP BY year, month, a.country WITH ROLLUP;