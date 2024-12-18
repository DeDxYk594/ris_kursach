DELIMITER $$

CREATE PROCEDURE `generate_sell_report` (
    IN p_year INT,
    IN p_month INT
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_goodtype_id INT;
    DECLARE v_units_sold INT;
    DECLARE v_money_sold INT;

    DECLARE cur_goodtypes CURSOR FOR
        SELECT goodtype_id FROM goodtype;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur_goodtypes;

    read_loop: LOOP
        FETCH cur_goodtypes INTO v_goodtype_id;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SELECT
            IFNULL(SUM(ol.quantity), 0) AS total_units,
            IFNULL(SUM(ol.quantity * IFNULL(ol.price, gt.sell_price)), 0) AS total_money
        INTO
            v_units_sold,
            v_money_sold
        FROM
            `orderline` ol
            JOIN `order` o ON ol.order_id = o.order_id
            JOIN `goodtype` gt ON ol.goodtype_id = gt.goodtype_id
        WHERE
            ol.goodtype_id = v_goodtype_id
            AND YEAR(o.created_at) = p_year
            AND MONTH(o.created_at) = p_month
            AND o.status IN ('paid', 'shipped');

        INSERT INTO `sell_report` (goodtype_id, year, month, units_sold, money_sold)
        VALUES (v_goodtype_id, p_year, p_month, v_units_sold, v_money_sold)
        ON DUPLICATE KEY UPDATE
            units_sold = VALUES(units_sold),
            money_sold = VALUES(money_sold);

    END LOOP;

    CLOSE cur_goodtypes;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE create_supply_report(
    IN p_year INT,
    IN p_month INT,
    OUT p_error TEXT
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_goodtype_id INT;
    DECLARE v_units_supplied INT;
    DECLARE v_money_supplied INT;

    DECLARE cur CURSOR FOR
        SELECT goodtype_id FROM goodtype;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SET p_error = '';

    proc: BEGIN
        IF (p_year > YEAR(CURDATE())) OR
           (p_year = YEAR(CURDATE()) AND p_month >= MONTH(CURDATE())) THEN
            SET p_error = 'Указанный месяц и год ещё не наступили.';
            LEAVE proc;
        END IF;

        OPEN cur;

        read_loop: LOOP
            FETCH cur INTO v_goodtype_id;
            IF done THEN
                LEAVE read_loop;
            END IF;

            SELECT
                IFNULL(SUM(supply_size), 0),
                IFNULL(SUM(supply_size * supply_unit_price), 0)
            INTO
                v_units_supplied,
                v_money_supplied
            FROM
                batch
            WHERE
                goodtype_id = v_goodtype_id
                AND YEAR(supplied_at) = p_year
                AND MONTH(supplied_at) = p_month;

            INSERT INTO supply_report (goodtype_id, year, month, units_supplied, money_supplied)
            VALUES (v_goodtype_id, p_year, p_month, v_units_supplied, v_money_supplied)
            ON DUPLICATE KEY UPDATE
                units_supplied = VALUES(units_supplied),
                money_supplied = VALUES(money_supplied);
        END LOOP;

        CLOSE cur;
    END proc;

END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE create_writeoff_report (
    IN p_year INT,
    IN p_month INT,
    OUT p_error TEXT
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_goodtype_id INT;
    DECLARE v_units_wrote INT;
    DECLARE v_money_wrote INT;

    -- Declare cursor for all goodtypes
    DECLARE cur_goodtypes CURSOR FOR
        SELECT goodtype_id FROM goodtype;

    -- Handler for cursor end
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Initialize error to empty string
    SET p_error = '';

    -- Validate input year and month
    IF p_year > YEAR(CURDATE()) OR
       (p_year = YEAR(CURDATE()) AND p_month >= MONTH(CURDATE())) OR
       p_month < 1 OR p_month > 12 THEN
        SET p_error = 'Invalid year or month. The specified period has not yet passed.';
        LEAVE proc_end;
    END IF;

    -- Optional: Start a transaction
    START TRANSACTION;

    -- Open the cursor
    OPEN cur_goodtypes;

    read_loop: LOOP
        FETCH cur_goodtypes INTO v_goodtype_id;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Calculate units_wrote and money_wrote for the given month and year
        SELECT
            COALESCE(SUM(quantity), 0),
            COALESCE(SUM(money), 0)
        INTO
            v_units_wrote,
            v_money_wrote
        FROM
            defect_writeoff
        WHERE
            goodtype_id = v_goodtype_id
            AND YEAR(defect_at) = p_year
            AND MONTH(defect_at) = p_month;

        -- Insert into writeoff_report
        INSERT INTO writeoff_report (goodtype_id, year, month, units_wrote, money_wrote)
        VALUES (v_goodtype_id, p_year, p_month, v_units_wrote, v_money_wrote)
        ON DUPLICATE KEY UPDATE
            units_wrote = VALUES(units_wrote),
            money_wrote = VALUES(money_wrote);
    END LOOP;

    -- Close the cursor
    CLOSE cur_goodtypes;

    -- Commit the transaction
    COMMIT;

    -- Exit point
    proc_end: BEGIN
        IF p_error <> '' THEN
            ROLLBACK;
        END IF;
    END;

END$$

DELIMITER ;
