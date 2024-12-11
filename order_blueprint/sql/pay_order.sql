UPDATE `order`
SET `status`='paid',
    paid_at=CURRENT_TIMESTAMP
WHERE order_id=%s;
