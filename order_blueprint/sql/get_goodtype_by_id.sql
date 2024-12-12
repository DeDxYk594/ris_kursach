SELECT gt.goodtype_id, gt.goodtype_id, gt.name,
    cat.category_name,
    gt.measure_unit,
    gt.has_units,
    gt.booked_units,
    gt.sell_price
FROM `goodtype` AS gt
JOIN category AS cat ON cat.category_id=gt.category_id
WHERE goodtype_id=%s;
