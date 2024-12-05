SELECT o.order_id, o.`status`, o.created_at,
l.orderline_id, l.quantity, COALESCE(l.price, l.quantity*g.sell_price),
g.article, g.name, g.measure_unit
FROM (SELECT ord.order_id, ord.`status`, ord.created_at
    FROM `order` AS ord
    JOIN external_user AS u ON u.customer_id=ord.customer_id
    WHERE u.ext_u_id=%s
    ORDER BY
    (CASE ord.`status`
        WHEN 'got_payment_unshipped' THEN 1
        WHEN 'booked' THEN 2
        WHEN 'unformed' THEN 3
        WHEN 'formed' THEN 4
        WHEN 'shipped' THEN 5
        ELSE 6 END)
    LIMIT 20 OFFSET %s)
AS o
LEFT JOIN orderline AS l ON l.order_id=o.order_id
LEFT JOIN goodtype AS g ON g.goodtype_id=l.goodtype_id;
