SELECT
FROM `order` AS o
JOIN external_user AS u ON u.customer_id=o.customer_id
WHERE u.ext_u_id=%s
ORDER BY
  CASE `status`
    WHEN 'got_payment_unshipped' THEN 1
    WHEN 'booked' THEN 2
    WHEN 'unformed' THEN 3
    WHEN 'formed' THEN 4
    WHEN 'shipped' THEN 5
    ELSE 6
LIMIT 20 OFFSET %s;
