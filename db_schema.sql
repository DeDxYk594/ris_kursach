CREATE TABLE IF NOT EXISTS `user` (
    u_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at DATE NOT NULL DEFAULT NOW(),
    updated_at DATE NOT NULL DEFAULT NOW(),
    role ENUM('customer','sales_manager','supply_manager','boss') NOT NULL,
    password_hash VARCHAR(100) NOT NULL
);
-- Сессия для Stateful авторизации
CREATE TABLE IF NOT EXISTS `session` (
    session_id VARCHAR(64) PRIMARY KEY, -- SHA256 HEX digest
    user_id INTEGER NOT NULL,
    user_id_fk FOREIGN KEY user_id REFERENCES TO user.u_id
);
CREATE TABLE IF NOT EXISTS `goodtype` (
    goodtype_id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(50) NOT NULL,
    measure_unit VARCHAR(20) NOT NULL
);
CREATE TABLE IF NOT EXISTS `customer` (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    address VARCHAR(50) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    contract_date DATE NOT NULL,
    bik VARCHAR(50) NOT NULL,
    acc_num VARCHAR(50) NOT NULL,
    bank_name VARCHAR(50) NOT NULL,
    total_ordered_quantity INTEGER DEFAULT 0 NOT NULL
);
CREATE TABLE IF NOT EXISTS `order` (
    order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    c_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    `status` ENUM(
        'unformed',
        'formed',
        'booked',
        'got_payment_unshipped',
        'shipped',
        'cancelled') DEFAULT 'unformed' NOT NULL,
    total_price INTEGER NOT NULL,
    pay_to_date DATE NOT NULL,
    fact_pay_date DATE,
    order_to_customer FOREIGN KEY c_id REFERENCES TO customer.c_id
);
-- good_batch - это партия товара, хранящаяся на складе
CREATE TABLE IF NOT EXISTS `good_batch` (
    s_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    g_id INTEGER NOT NULL,
    unit_price INTEGER NOT NULL,
    locked INTEGER DEFAULT 0 NOT NULL,
    last_locked_date DATE,
    stored_ INTEGER DEFAULT 0 NOT NULL,
    last_cargo_date DATE,
    storedgood_to_goodtype FOREIGN KEY g_id REFERENCES TO goodtype.goodtype_id
);
CREATE TABLE IF NOT EXISTS `orderline` (
    l_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    g_id INTEGER NOT NULL,
    z_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    line_to_goodtype FOREIGN KEY g_id REFERENCES TO goodtype.g_id,
    line_to_order FOREIGN KEY order_id REFERENCES TO order.order_id
);

-- Таблицы для отчётов
CREATE TABLE IF NOT EXISTS `dim_time` (
    dim_time_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    year INTEGER NOT NULL,
    month INTEGER,
    day INTEGER
);
CREATE TABLE IF NOT EXISTS `dim_goodtype` (
    dim_goodtype_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    goodtype_id INTEGER,
    category_id INTEGER
);
CREATE TABLE `fct_sales_report` (
    dim_time_id INTEGER,
    dim_goodtype_id INTEGER,
    PRIMARY KEY (dim_time_id, dim_goodtype_id)
);
CREATE TABLE `fct_supply_report` (

);
