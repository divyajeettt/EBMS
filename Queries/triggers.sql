
-- trigger to create a wallet for a new customer

DROP TRIGGER IF EXISTS create_wallet;
DELIMITER $$
CREATE TRIGGER create_wallet AFTER INSERT ON customer
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT * FROM wallet WHERE customerID = NEW.customerID) THEN
        INSERT INTO wallet (customerID, balance) VALUES (NEW.customerID, 0);
    END IF;
END;
$$
DELIMITER ;


-- sample query to test the above trigger
INSERT INTO customer (name, email, phone, address) VALUES ('test', 'test@example.com', '1234567890', 'test address');
SELECT * FROM wallet;



-- trigger to change da's availability to false when he is assigned to an order

DROP TRIGGER IF EXISTS da_unavailable;
DELIMITER $$
CREATE TRIGGER da_unavailable AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    UPDATE delivery_agent SET avalability = FALSE WHERE daID = NEW.daID;
END;
$$
DELIMITER ;

-- sample query to test the above trigger
SELECT * FROM delivery_agent WHERE daID = 1;
INSERT INTO orders (customerID, daID, order_date) VALUES (202, 1, '2020-12-12'); -- check orderID and daID in this query
SELECT * FROM delivery_agent WHERE daID = 1;



-- trigger to change the availability of da to true when he completes an order

DROP TRIGGER IF EXISTS da_available;
DELIMITER $$
CREATE TRIGGER da_available AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT * FROM orders WHERE daID = NEW.daID AND delivery_date IS NULL) THEN
        UPDATE delivery_agent SET avalability = TRUE WHERE daID = NEW.daID;
    END IF;
END;
$$
DELIMITER ;

-- sample query to test the above trigger
SELECT * FROM delivery_agent WHERE daID = 1;
UPDATE orders SET order_date = '2020-12-12' WHERE orderID = 1; -- check orderID and daID in this query
SELECT * FROM delivery_agent WHERE daID = 1;