SELECT COUNT(*)
FROM `order` AS o
JOIN external_user AS u ON u.customer_id=o.customer_id
WHERE o.customer_id=%s;
