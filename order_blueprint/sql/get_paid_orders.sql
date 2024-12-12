SELECT o.order_id, o.`status`, o.created_at,
l.orderline_id, l.quantity, COALESCE(l.price, l.quantity*g.sell_price),
g.goodtype_id, g.name, g.measure_unit, c.name
FROM (SELECT ord.order_id, ord.`status`, ord.created_at, ord.customer_id
    FROM `order` AS ord
    JOIN external_user AS u ON u.customer_id=ord.customer_id
    WHERE ord.status ='got_payment_unshipped'
    LIMIT 20 OFFSET %s)
AS o
LEFT JOIN orderline AS l ON l.order_id=o.order_id
LEFT JOIN goodtype AS g ON g.goodtype_id=l.goodtype_id
JOIN customer AS c USING(customer_id)
ORDER BY o.order_id;
