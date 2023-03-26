-- trigger to check if quantity in order is less than or equal to product quantity from order_product

DROP TRIGGER IF EXISTS check_product_qty;
DELIMITER $$
CREATE TRIGGER check_product_qty BEFORE INSERT ON order_product
FOR EACH ROW
BEGIN
    DECLARE product_qty INT;
    DECLARE order_product_id INT;
    DECLARE order_product_qty INT;
    DECLARE done INT DEFAULT FALSE;
    SELECT quantity INTO product_qty FROM product WHERE productID = NEW.productID;
    IF (product_qty < NEW.quantity) THEN
        
    END IF;
END;
$$
DELIMITER ;


    DECLARE cur CURSOR FOR SELECT productID, quantity FROM order_product WHERE orderID = NEW.orderID;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO order_product_id, order_product_qty;
        IF done THEN
            LEAVE read_loop;
        END IF;
        SELECT quantity INTO product_qty FROM product WHERE productID = order_product_id;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'working';
        IF (product_qty < order_product_qty) THEN
            DELETE FROM order_product WHERE orderID = NEW.orderID;
            DELETE FROM orders WHERE orderID = NEW.orderID;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity in order is more than available quantity';
        END IF;
    END LOOP;
    CLOSE cur;
END;
$$
DELIMITER ;

-- sample query to test the above trigger
INSERT INTO orders (customerID, daID, order_date) VALUES (202, 1, '2020-12-12');
INSERT INTO order_product (orderID, productID, quantity) VALUES (1, 1, 1000000);




-- trigger to create a wallet for a new customer

DROP TRIGGER IF EXISTS create_wallet;
DELIMITER $$
CREATE TRIGGER create_wallet AFTER INSERT ON customer
FOR EACH ROW
BEGIN
    INSERT INTO wallet (customerID, balance) VALUES (NEW.customerID, 0);
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
INSERT INTO orders (customerID, daID, order_date) VALUES (202, 1, '2020-12-12');
SELECT * FROM delivery_agent WHERE daID = 1;



-- trigger to change the availability of da to true when he completes an order

DROP TRIGGER IF EXISTS da_available;
DELIMITER $$
CREATE TRIGGER da_available AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    UPDATE delivery_agent SET avalability = true WHERE daID = NEW.daID;
END;
$$
DELIMITER ;