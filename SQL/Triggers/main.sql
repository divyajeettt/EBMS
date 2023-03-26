-- Trigger-01: Create a wallet for a new customer as soon as a customer is created
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

-- Helper queries to test Trigger create_wallet

-- Create a new customer
INSERT INTO customer (name, email, phone, address)
VALUES ('test', 'test@example.com', '1234567890', 'test address');

-- Check if a wallet is created for the new customer
SELECT * FROM wallet WHERE customerID = (SELECT MAX(customerID) FROM customer);

---------------------------------------------------------------------------------------------------------------------------------

-- Trigger-02: Change a delivery agent's availability to False when they are assigned to an order
DROP TRIGGER IF EXISTS da_unavailable;
DELIMITER $$
CREATE TRIGGER da_unavailable AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    UPDATE delivery_agent SET avalability = FALSE WHERE daID = NEW.daID;
END;
$$
DELIMITER ;

-- Helper queries to test Trigger da_unavailable

-- Check the availability of a specific delivery agent
SELECT daID, availability FROM delivery_agent WHERE daID = 1;

-- Assign an order to that delivery agent [check orderID in this query]
INSERT INTO orders (customerID, daID, order_date) VALUES (202, 1, '2020-12-12');

-- Check the availability of the delivery agent
SELECT daID, availability FROM delivery_agent WHERE daID = 1;

---------------------------------------------------------------------------------------------------------------------------------

-- Trigger-03: Change a delivery agent's availability to True when they complete an order
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

-- Helper queries to test Trigger da_available

-- Check the availability of a delivery agent who is assigned to an order
SELECT daID, availability FROM delivery_agent WHERE daID = 1;

-- Complete the order [use the orderID from the previous Trigger]
UPDATE orders SET order_date = '2020-12-12' WHERE orderID = 1;

-- Check the availability of the delivery agent
SELECT * FROM delivery_agent WHERE daID = 1;