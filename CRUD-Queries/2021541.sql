-- CREATE

-- READ
SELECT p.productID, p.name, AVG(pr.rating) FROM product_review pr, product p WHERE p.productID = pr.productID GROUP BY p.productID ORDER BY AVG(pr.rating) DESC;

SELECT p.productID, p.name, pr.rating FROM product_review pr, product p WHERE p.productID = pr.productID AND pr.rating = 5;

SELECT da.daID, da.first_name, da.middle_initial, da.last_name, AVG(dr.rating) FROM da_review dr, delivery_agent da WHERE da.daID = dr.daID GROUP BY da.daID ORDER BY AVG(dr.rating) DESC;

SELECT da.daID, da.first_name, da.middle_initial, da.last_name, dr.rating FROM da_review dr, delivery_agent da WHERE da.daID = dr.daID AND dr.rating = 5;

-- UPDATE

UPDATE address SET apt_number = '100' WHERE addressID = (SELECT addressID FROM customer WHERE customerID = 1);

-- DELETE