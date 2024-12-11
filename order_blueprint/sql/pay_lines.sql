UPDATE orderline AS l
JOIN goodtype AS g ON g.goodtype_id = l.goodtype_id
SET l.price = l.quantity * g.sell_price
WHERE l.order_id = %s;
