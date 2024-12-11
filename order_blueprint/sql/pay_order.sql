UPDATE `order`
SET `status`='got_payment_unshipped',
    paid_at=CURRENT_TIMESTAMP
WHERE order_id=%s;
