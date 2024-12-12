
DROP PROCEDURE IF EXISTS add_common_report;

DELIMITER //

CREATE PROCEDURE add_common_report(
    IN p_goodtype_id INT,
    IN p_year INT,
    IN p_month INT,
    IN p_day INT,
    OUT p_error VARCHAR(255)
)
BEGIN
    DECLARE report_date DATE;
    DECLARE v_units_sold INT;
    DECLARE v_money_sold INT;
    DECLARE v_units_supplied INT;
    DECLARE v_money_supplied INT;
    DECLARE v_units_wrote INT;
    DECLARE v_money_wrote INT;
    DECLARE v_sell_price INT;

    -- Инициализация сообщения об ошибке
    SET p_error = '';

    -- Формирование даты отчета
    SET report_date = STR_TO_DATE(CONCAT(p_year, '-', p_month, '-', p_day), '%Y-%m-%d');

    proc_end: BEGIN
    -- Проверка корректности даты
    IF report_date IS NULL THEN
        SET p_error = 'Неверная дата.';
        LEAVE proc_end;
    END IF;

    -- Шаг 1: Проверка, что дата уже прошла
    IF report_date >= CURDATE() THEN
        SET p_error = 'Дата должна быть в прошлом.';
        LEAVE proc_end;
    END IF;

    -- Шаг 2: Проверка, что отчёт на эту дату и товар ещё не существует
    IF EXISTS (
        SELECT 1 FROM common_report
        WHERE goodtype_id = p_goodtype_id
            AND year = p_year
            AND month = p_month
            AND day = p_day
    ) THEN
        SET p_error = 'Отчёт за эту дату и товар уже существует.';
        LEAVE proc_end;
    END IF;

    -- Шаг 3.1: Расчёт units_sold и money_sold
    SELECT IFNULL(SUM(l.quantity), 0), IFNULL(SUM(l.price), 0)
    INTO v_units_sold, v_money_sold
    FROM `order` o
    JOIN orderline l ON o.order_id = l.order_id
    WHERE o.paid_at IS NOT NULL
        AND DAY(o.paid_at)=p_day
        AND MONTH(o.paid_at)=p_month
        AND YEAR(o.paid_at)=p_year
        AND l.goodtype_id = p_goodtype_id;

    -- Шаг 3.2: Расчёт units_supplied и money_supplied
    SELECT IFNULL(SUM(b.supply_size), 0), IFNULL(SUM(b.supply_size * b.supply_unit_price), 0)
    INTO v_units_supplied, v_money_supplied
    FROM batch b
    WHERE b.goodtype_id = p_goodtype_id
        AND DAY(b.supplied_at)=p_day
        AND MONTH(b.supplied_at)=p_month
        AND YEAR(b.supplied_at)=p_year;

    -- Получение sell_price из таблицы goodtype
    SELECT sell_price INTO v_sell_price
    FROM goodtype
    WHERE goodtype_id = p_goodtype_id;

    -- Шаг 3.3: Расчёт units_wrote
    SELECT IFNULL(SUM(dw.quantity), 0)
    INTO v_units_wrote
    FROM defect_writeoff dw
    WHERE dw.goodtype_id = p_goodtype_id
        AND DAY(dw.defect_at)=p_day
        AND MONTH(dw.defect_at)=p_month
        AND YEAR(dw.defect_at)=p_year;

    -- Расчёт money_wrote
    SET v_money_wrote = v_units_wrote * v_sell_price;

    -- Шаг 4: Вставка данных в таблицу common_report
    INSERT INTO common_report (
        goodtype_id, year, month, day,
        units_sold, money_sold,
        units_supplied, money_supplied,
        units_wrote, money_wrote
    ) VALUES (
        p_goodtype_id, p_year, p_month, p_day,
        v_units_sold, v_money_sold,
        v_units_supplied, v_money_supplied,
        v_units_wrote, v_money_wrote
    );

    -- Метка завершения процедуры
    END proc_end;
END //

DELIMITER ;
