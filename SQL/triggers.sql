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
-- CHECK USING THE FRONT-END

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

-- Helper queries to test Trigger da_available (Can also be tested directly through the front-end)
INSERT INTO orders (customerID, daID, order_date) VALUES (1, 201, '2020-12-12');
INSERT INTO orders (customerID, daID, order_date) VALUES (2, 201, '2020-11-13');
INSERT INTO orders (customerID, daID, order_date) VALUES (3, 201, '2020-10-14');
-- Check the availability of a delivery agent who is assigned to an order
SELECT * FROM delivery_agent WHERE daID = 201;
SELECT * FROM orders WHERE daID = 201;

-- Complete one of the orders assigned to that delivery agent
UPDATE orders SET delivery_date = CURDATE() WHERE orderID = 88;

-- Complete all orders
UPDATE orders SET delivery_date = CURDATE() WHERE daID=1;

-- Check the availability of the delivery agent
SELECT * FROM delivery_agent WHERE daID = 1;
SELECT * FROM orders WHERE daID = 1;

-- Revert the changes
UPDATE orders SET delivery_date = NULL WHERE orderID = 88;
UPDATE orders SET delivery_date = "2022-06-03" WHERE orderID = 311;
UPDATE orders SET delivery_date = NULL WHERE orderID = 634;
UPDATE orders SET delivery_date = NULL WHERE orderID = 741;
-- since in the implementation, the delivery_date is never set back to NULL, we won't use the trigger to set the availability to FALSE
UPDATE delivery_agent SET avalability = FALSE WHERE daID = 1;