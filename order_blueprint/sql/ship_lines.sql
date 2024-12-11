UPDATE goodtype AS g
JOIN orderline AS l ON l.goodtype_id=g.goodtype_id
SET g.booked_units=g.booked_units-l.quantity,
    g.has_units=g.has_units-l.quantity
WHERE l.order_id=%s;
