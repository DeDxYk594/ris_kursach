SELECT order_id
FROM `order` AS o
JOIN external_user AS u ON u.customer_id=o.customer_id
WHERE u.ext_u_id=%s AND o.order_id=%s;
