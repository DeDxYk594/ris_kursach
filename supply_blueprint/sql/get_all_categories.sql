SELECT cat.category_id, cat.category_name, COALESCE(COUNT(gt.goodtype_id),0)
FROM `category` AS cat
LEFT JOIN `goodtype` AS gt ON gt.category_id=cat.category_id
WHERE COALESCE(gt.is_hidden,FALSE)=FALSE
GROUP BY cat.category_id;
