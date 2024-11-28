SELECT cat.category_id, cat.category_name, COUNT(*)
FROM `category` AS cat
JOIN `goodtype` AS gt ON gt.category_id=cat.category_id
WHERE gt.is_hidden=FALSE
GROUP BY cat.category_id;
