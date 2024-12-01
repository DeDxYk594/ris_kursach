SELECT gt.goodtype_id, gt.article, gt.name,
    gt.category_id,
    gt.measure_unit,
    gt.has_units,
    gt.sell_price
FROM goodtype AS gt
JOIN category AS cat ON cat.category_id=gt.category_id
WHERE gt.is_hidden=FALSE
    AND lower(gt.name) LIKE %s
    AND (gt.category_id=%s OR %s IS NULL)
    AND (gt.sell_price<=%s OR %s IS NULL)
    AND (gt.sell_price>=%s OR %s IS NULL)
GROUP BY gt.goodtype_id
ORDER BY gt.goodtype_id
LIMIT 20 OFFSET %s;
