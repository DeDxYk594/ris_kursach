import json
import pymysql
from faker import Faker
import random
from datetime import datetime
import sys

# Параметры подключения к базе данных
with open("../db_config.json", "r", encoding="utf-8") as f:
    db_config = json.loads(f.read())


def generate_categories(fake, num=10):
    categories = set()
    while len(categories) < num:
        category = fake.word().capitalize()
        categories.add(category)
    return list(categories)


def generate_goodtypes(fake, categories, num=1000):
    measure_units = ["шт", "кг", "л", "м", "пар", "упаковка", "метр"]
    goodtypes = []
    for _ in range(num):
        article = random.randint(1000, 9999)
        name = fake.word().capitalize()
        category_id = random.randint(1, len(categories))
        is_hidden = random.choice([True, False])
        measure_unit = random.choice(measure_units)
        has_units = random.randint(1, 100)
        booked_units = random.randint(0, has_units)
        sell_price = random.randint(100, 10000)
        goodtypes.append(
            (
                article,
                name,
                category_id,
                is_hidden,
                measure_unit,
                has_units,
                booked_units,
                sell_price,
            )
        )
    return goodtypes


def generate_batches(fake, num=3000, goodtype_total=1000):
    batches = []
    for _ in range(num):
        supplied_at = fake.date_time_between(start_date="-2y", end_date="now")
        # Обновлено не раньше, чем поставлено
        updated_at = fake.date_time_between(start_date=supplied_at, end_date="now")
        supply_unit_price = random.randint(50, 5000)
        supply_size = random.randint(10, 1000)
        units_left = random.randint(0, supply_size)
        goodtype_id = random.randint(1, goodtype_total)
        batches.append(
            (
                supplied_at.strftime("%Y-%m-%d %H:%M:%S"),
                updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                supply_unit_price,
                supply_size,
                units_left,
                goodtype_id,
            )
        )
    return batches


def main():
    # Инициализация Faker с русской локалью
    fake = Faker("ru_RU")

    try:
        # Подключение к базе данных
        connection = pymysql.connect(**db_config)
        print("Подключение к базе данных успешно.")

        with connection.cursor() as cursor:
            # Генерация и вставка категорий
            categories = generate_categories(fake, num=10)
            category_data = [(category,) for category in categories]
            insert_category_query = (
                "INSERT INTO `category` (`category_name`) VALUES (%s);"
            )
            cursor.executemany(insert_category_query, category_data)
            connection.commit()
            print(f"Вставлено {len(category_data)} категорий.")

            # Генерация и вставка типов товаров
            goodtypes = generate_goodtypes(fake, categories, num=1000)
            insert_goodtype_query = """
                INSERT INTO `goodtype`
                (`article`, `name`, `category_id`, `is_hidden`, `measure_unit`, `has_units`, `booked_units`, `sell_price`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.executemany(insert_goodtype_query, goodtypes)
            connection.commit()
            print(f"Вставлено {len(goodtypes)} типов товаров.")

            # Генерация и вставка партий товаров
            batches = generate_batches(fake, num=3000, goodtype_total=1000)
            insert_batch_query = """
                INSERT INTO `batch`
                (`supplied_at`, `updated_at`, `supply_unit_price`, `supply_size`, `units_left`, `goodtype_id`)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.executemany(insert_batch_query, batches)
            connection.commit()
            print(f"Вставлено {len(batches)} партий товаров.")

    except pymysql.MySQLError as e:
        print(f"Ошибка при работе с MySQL: {e}")
        sys.exit(1)
    finally:
        if connection:
            connection.close()
            print("Соединение с базой данных закрыто.")


if __name__ == "__main__":
    main()
