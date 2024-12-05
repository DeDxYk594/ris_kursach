INSERT INTO `order` (customer_id, total_price, pay_to_date)
VALUES (
    (SELECT customer_id FROM external_user WHERE ext_u_id=%s),
    0,
    TIMESTAMPADD(DAY, 3, CURRENT_TIMESTAMP)
);
