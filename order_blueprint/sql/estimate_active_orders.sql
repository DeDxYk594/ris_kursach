SELECT COUNT(*)
FROM `order` AS o
WHERE o.`status` IN ('unformed', 'got_payment_unshipped');
