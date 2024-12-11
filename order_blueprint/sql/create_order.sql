INSERT INTO `order` (customer_id, pay_to_date)
VALUES (
    (SELECT customer_id FROM external_user WHERE ext_u_id=%s),
    TIMESTAMPADD(DAY, 3, CURRENT_TIMESTAMP)
);
