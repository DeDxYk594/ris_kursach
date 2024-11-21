CREATE TABLE IF NOT EXISTS `user` (
    u_id       INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
    username   TEXT    UNIQUE NOT NULL,
    real_name  TEXT    NOT NULL,
    created_at DATE    NOT NULL DEFAULT NOW(),
    updated_at DATE    NOT NULL DEFAULT NOW(),
    role ENUM('customer','sales_manager','supply_manager','boss') NOT NULL,
    password_hash TEXT NOT NULL
);

-- Сессия для Stateful авторизации
CREATE TABLE IF NOT EXISTS `session` (
    session_id  TEXT    PRIMARY KEY, -- SHA256 HEX digest
    u_id        INTEGER NOT NULL,
    valid_until DATETIME,

    user_id_fk FOREIGN KEY user_id REFERENCES TO user.u_id ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `goodtype` (
    goodtype_id  INTEGER PRIMARY KEY NOT NULL,
    name         TEXT    NOT NULL,
    measure_unit TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `customer` (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    address       TEXT    NOT NULL,
    phone         TEXT    NOT NULL,
    contract_date DATE    NOT NULL,
    bik           TEXT    NOT NULL,
    acc_num       TEXT    NOT NULL,
    bank_name     TEXT    NOT NULL,
    money_spent   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS `order` (
    order_id     INTEGER  PRIMARY KEY AUTO_INCREMENT,
    customer_id  INTEGER  NOT NULL,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME NOT NULL,
    `status` ENUM(
        'unformed',
        'formed',
        'booked',
        'got_payment_unshipped',
        'shipped',
        'cancelled')       NOT NULL DEFAULT 'unformed',
    total_price   INTEGER  NOT NULL,
    pay_to_date   DATE     NOT NULL,
    paid_at       DATETIME,

    order_to_customer FOREIGN KEY c_id REFERENCES TO customer.c_id
);

-- batch - это партия товара, хранящаяся на складе
CREATE TABLE IF NOT EXISTS `batch` (
    batch_id          INTEGER  PRIMARY KEY AUTO_INCREMENT,
    supplied_at       DATETIME NOT NULL,
    updated_at        DATETIME NOT NULL,
    supply_unit_price INTEGER  NOT NULL,
    supply_size       INTEGER  NOT NULL,
    units_left        INTEGER  NOT NULL,
    goodtype_id       INTEGER  NOT NULL,

    goodtype_id_fk FOREIGN KEY goodtype_id REFERENCES TO goodtype.goodtype_id
);

CREATE TABLE IF NOT EXISTS `orderline` (
    orderline_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    goodtype_id  INTEGER NOT NULL,
    order_id     INTEGER NOT NULL,
    quantity     INTEGER NOT NULL,
    price        INTEGER, -- выставляется только при оплате, хранится для статистики

    goodtype_id_fk FOREIGN KEY g_id REFERENCES TO goodtype.g_id,
    order_id_fk    FOREIGN KEY order_id REFERENCES TO order.order_id
);

CREATE TABLE IF NOT EXISTS `defect_writeoff` (
    dw_id     INTEGER  PRIMARY KEY AUTO_INCREMENT,
    batch_id  INTEGER  NOT NULL,
    quantity  INTEGER  NOT NULL,
    defect_at DATETIME NOT NULL,

    batch_id_fk FOREIGN KEY batch_id REFERENCES TO batch.batch_id
);

-- Таблицы для отчётов
CREATE TABLE IF NOT EXISTS `dim_time` (
    dim_time_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    year        INTEGER NOT NULL,
    month       INTEGER,
    day         INTEGER
);
CREATE TABLE IF NOT EXISTS `dim_goodtype` (
    dim_goodtype_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    goodtype_id     INTEGER,
    category_id     INTEGER
);
CREATE TABLE `fct_sales_report` (
    dim_time_id     INTEGER,
    dim_goodtype_id INTEGER,
    units_sold      INTEGER NOT NULL,
    money_sold      INTEGER NOT NULL,
    units_supplied  INTEGER NOT NULL,
    money_supplied  INTEGER NOT NULL,

    PRIMARY KEY (dim_time_id, dim_goodtype_id)
);
