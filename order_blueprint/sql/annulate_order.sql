UPDATE `order`
SET `status` = 'cancelled'
WHERE `order_id`=%s;
