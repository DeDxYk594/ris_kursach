SELECT COUNT(*)
FROM goodtype AS gt
WHERE gt.is_hidden=FALSE
    AND lower(gt.name) LIKE %s
    AND (gt.category_id=%s OR %s IS NULL)
    AND (gt.sell_price<=%s OR %s IS NULL)
    AND (gt.sell_price>=%s OR %s IS NULL);
