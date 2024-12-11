UPDATE `order`
SET `status`='shipped'
WHERE order_id=%s;
