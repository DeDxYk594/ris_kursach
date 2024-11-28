-- Пользователь, который может залогиниться
CREATE TABLE IF NOT EXISTS `user` (
    u_id       INTEGER     PRIMARY KEY AUTO_INCREMENT,
    username   VARCHAR(30) UNIQUE NOT NULL,
    real_name  TEXT        NOT NULL,
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    role ENUM('customer','sales_manager','supply_manager','boss') NOT NULL,
    password_hash TEXT     NOT NULL
);

-- Сессия для Stateful авторизации
CREATE TABLE IF NOT EXISTS `session` (
    session_id  VARCHAR(64) PRIMARY KEY, -- SHA256 HEX digest
    u_id        INTEGER     NOT NULL,
    valid_until DATETIME    NOT NULL,

    FOREIGN KEY (u_id) REFERENCES `user` (u_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Категория товара
CREATE TABLE IF NOT EXISTS `category` (
    category_id   INTEGER PRIMARY KEY AUTO_INCREMENT,
    category_name TEXT    NOT NULL
);

-- Номенклатура товара
CREATE TABLE IF NOT EXISTS `goodtype` (
    goodtype_id  INTEGER PRIMARY KEY AUTO_INCREMENT,
    article      INTEGER NOT NULL,
    name         TEXT    NOT NULL,
    category_id  INTEGER NOT NULL,
    is_hidden    BOOLEAN NOT NULL DEFAULT FALSE,
    measure_unit TEXT    NOT NULL,
    has_units    INTEGER NOT NULL,
    booked_units INTEGER NOT NULL,
    sell_price   INTEGER NOT NULL,

    FOREIGN KEY (category_id) REFERENCES `category` (category_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Покупатель
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

-- Заказ
CREATE TABLE IF NOT EXISTS `order` (
    order_id     INTEGER  PRIMARY KEY AUTO_INCREMENT,
    customer_id  INTEGER  NOT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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

    FOREIGN KEY (customer_id) REFERENCES `customer` (customer_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Партия товара, хранящаяся на складе
CREATE TABLE IF NOT EXISTS `batch` (
    batch_id          INTEGER  PRIMARY KEY AUTO_INCREMENT,
    supplied_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL,
    supply_unit_price INTEGER  NOT NULL,
    supply_size       INTEGER  NOT NULL,
    units_left        INTEGER  NOT NULL,
    goodtype_id       INTEGER  NOT NULL,

    FOREIGN KEY (goodtype_id) REFERENCES `goodtype` (goodtype_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Строка заказа
CREATE TABLE IF NOT EXISTS `orderline` (
    orderline_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    goodtype_id  INTEGER NOT NULL,
    order_id     INTEGER NOT NULL,
    quantity     INTEGER NOT NULL,
    price        INTEGER, -- выставляется только при оплате, хранится для статистики

    FOREIGN KEY (goodtype_id) REFERENCES goodtype (goodtype_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES `order` (order_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Списание товара из-за дефекта
CREATE TABLE IF NOT EXISTS `defect_writeoff` (
    dw_id     INTEGER  PRIMARY KEY AUTO_INCREMENT,
    batch_id  INTEGER  NOT NULL,
    quantity  INTEGER  NOT NULL,
    defect_at DATETIME NOT NULL,
    reason    TEXT     NOT NULL,

    FOREIGN KEY (batch_id) REFERENCES `batch` (batch_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица измерения по времени для отчётов
CREATE TABLE IF NOT EXISTS `dim_time` (
    dim_time_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    year        INTEGER NOT NULL,
    month       INTEGER,
    day         INTEGER
);

-- Таблица измерения по виду товара для отчётов
CREATE TABLE IF NOT EXISTS `dim_goodtype` (
    dim_goodtype_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    goodtype_id     INTEGER,
    category_id     INTEGER
);

-- Таблица фактов для отчётов
CREATE TABLE `fct_sales_report` (
    dim_time_id     INTEGER,
    dim_goodtype_id INTEGER,
    units_sold      INTEGER NOT NULL,
    money_sold      INTEGER NOT NULL,
    units_supplied  INTEGER NOT NULL,
    money_supplied  INTEGER NOT NULL,

    PRIMARY KEY (dim_time_id, dim_goodtype_id),
    FOREIGN KEY (dim_time_id) REFERENCES `dim_time` (dim_time_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (dim_goodtype_id) REFERENCES `dim_goodtype` (dim_goodtype_id) ON UPDATE CASCADE ON DELETE CASCADE
);
