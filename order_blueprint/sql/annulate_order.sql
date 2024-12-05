UPDATE `order`
SET `status` = 'cancelled'
WHERE `order_id` IN (
    SELECT `order_id` FROM (
        SELECT o.`order_id`
        FROM `order` AS o
        JOIN `external_user` AS u ON u.`customer_id` = o.`customer_id`
        WHERE o.`order_id` = %s AND u.`ext_u_id` = %s
    ) AS temp_table
);
