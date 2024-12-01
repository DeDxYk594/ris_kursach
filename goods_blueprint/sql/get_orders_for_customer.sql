SELECT
FROM order AS o
JOIN customer AS c ON o.customer_id=c.customer_id
JOIN user AS u ON u.customer_id=
