SELECT COUNT(*)
FROM `order` AS o
WHERE o.`status`='got_payment_unshipped';
