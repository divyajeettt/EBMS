-- CREATE



-- READ

-- show all suppliers who have the average rating of their products above (or equal to 4);
SELECT s.supplierID, s.first_name, s.middle_initial, s.last_name, avg(rating) FROM supplier s, product_review 
    WHERE s.supplierID = (SELECT supplierID FROM product WHERE product_review.productID = product.productID AND product.supplierID=s.supplierID)
    AND NOT EXISTS ((SELECT avg(rating) FROM product_review, product WHERE product_review.productID = product.productID AND product.supplierID = s.supplierID) EXCEPT (SELECT avg(rating) from product_review GROUP BY productID HAVING avg(rating) >= 4))
    GROUP BY s.supplierID;
-- this is incorrect ^^

-- show all suppliers who have all their products with rating above (or equal to) 4;
SELECT s.supplierID, s.first_name, s.middle_initial, s.last_name FROM supplier s
WHERE NOT EXISTS ( (
        SELECT avg(rating) FROM product_review, product WHERE product_review.productID = product.productID AND product.supplierID = s.supplierID
    ) EXCEPT (
        SELECT avg(rating) from product_review GROUP BY productID HAVING avg(rating) >= 4
    )
);


-- show all suppliers that do not sell any products
SELECT s.supplierID, s.first_name, s.middle_initial, s.last_name FROM supplier s
WHERE NOT EXISTS (SELECT * FROM product WHERE product.supplierID = s.supplierID);


-- show all products that have the average rating above (or equal to) 3.5, ordered by the average rating;
SELECT p.productID, p.name, AVG(pr.rating) FROM product_review pr, product p
WHERE p.productID = pr.productID
GROUP BY p.productID HAVING AVG(pr.rating) >= 3.5
ORDER BY AVG(pr.rating) DESC;


-- SELECT p.productID, p.name, pr.rating FROM product_review pr, product p WHERE p.productID = pr.productID AND pr.rating = 5;

SELECT da.daID, da.first_name, da.middle_initial, da.last_name, AVG(dr.rating) FROM da_review dr, delivery_agent da WHERE da.daID = dr.daID GROUP BY da.daID ORDER BY AVG(dr.rating) DESC;

SELECT da.daID, da.first_name, da.middle_initial, da.last_name, dr.rating FROM da_review dr, delivery_agent da WHERE da.daID = dr.daID AND dr.rating = 5;

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

-- DELETE