-- CREATE

-- READ

-- show all suppliers who have the average rating of their products above (or equal to 4);
SELECT s.supplierID, CONCAT(s.first_name, ' ', s.middle_initial, ' ', s.last_name) AS Name, avg(rating) FROM supplier s, product_review 
    WHERE s.supplierID = (SELECT supplierID FROM product WHERE product_review.productID = product.productID AND product.supplierID=s.supplierID)
    AND NOT EXISTS ((SELECT avg(rating) FROM product_review, product WHERE product_review.productID = product.productID AND product.supplierID = s.supplierID) EXCEPT (SELECT avg(rating) FROM product_review GROUP BY productID HAVING avg(rating) >= 4))
    GROUP BY s.supplierID;
-- this is incorrect ^^


-- UPDATE

-- DELETE

-- delete products that have average rating below 2 and more than 2 reviews
DELETE FROM product
WHERE productID IN (
    SELECT pID FROM (
        SELECT p.productID AS pID FROM product_review pr, product p
        WHERE p.productID = pr.productID
        AND NOT EXISTS (
            SELECT c.productID FROM cart AS c
            WHERE p.productID = c.productID
        )
        GROUP BY p.productID
        HAVING AVG(pr.rating) < 2 AND COUNT(pr.rating) > 2
    ) AS t    
);

-- auxiliary query for checking deletion
SELECT productID, avg(rating), count(rating) FROM product_review GROUP BY productID HAVING avg(rating) < 2 AND count(rating) > 2;