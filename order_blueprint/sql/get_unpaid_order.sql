SELECT o.order_id, o.`status`, o.created_at,
l.orderline_id, l.quantity, COALESCE(l.price, l.quantity*g.sell_price),
g.article, g.name, g.measure_unit, c.name
FROM `order` AS o
LEFT JOIN orderline AS l ON l.order_id=o.order_id
LEFT JOIN goodtype AS g ON g.goodtype_id=l.goodtype_id
JOIN customer AS c USING(customer_id)
WHERE o.order_id=%s AND o.`status`='unpaid'
ORDER BY o.order_id;
