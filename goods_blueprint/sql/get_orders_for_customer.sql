SELECT o.order_id
FROM `order` AS o
JOIN customer AS c ON o.customer_id=c.customer_id
JOIN external_user AS u ON u.customer_id=c.customer_id
WHERE o.customer_id=%s
AND o.status='unformed';
