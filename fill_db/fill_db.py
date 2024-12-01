# Initialize Faker with Russian locale
import json
import random
from faker import Faker
import pymysql

with open("../db_config.json") as f:
    db_config = json.load(f)


fake = Faker("ru_RU")


def get_ids(cursor, table, id_field="id"):
    cursor.execute(f"SELECT {id_field} FROM `{table}`")
    return [row[0] for row in cursor.fetchall()]


def get_random_id(id_list):
    return random.choice(id_list) if id_list else None


def main():
    try:
        # Connect to the database
        connection = pymysql.connect(
            **db_config,
            autocommit=False,  # Manage transactions manually
        )

        with connection.cursor() as cursor:
            ### Step 1: Insert 100 Customers ###
            print("Inserting 100 customers...")
            customers = []
            for customer_id in range(1, 101):
                name = fake.company()
                address = fake.address().replace("\n", ", ")
                phone = fake.phone_number()
                contract_date = fake.date_between(start_date="-2y", end_date="today")
                bik = "".join([str(random.randint(0, 9)) for _ in range(9)])
                acc_num = "".join([str(random.randint(0, 9)) for _ in range(20)])
                bank_name = 'ООО "' + fake.company() + ' Банк"'
                money_spent = random.randint(0, 1000000)
                customers.append(
                    (
                        customer_id,
                        name,
                        address,
                        phone,
                        contract_date,
                        bik,
                        acc_num,
                        bank_name,
                        money_spent,
                    )
                )

            insert_customer_query = """
                INSERT INTO `customer`
                (customer_id, name, address, phone, contract_date, bik, acc_num, bank_name, money_spent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_customer_query, customers)
            connection.commit()
            customer_ids = get_ids(cursor, "customer", "customer_id")
            print("Inserted 100 customers.")

            ### Step 2: Insert 10 Categories ###
            print("Inserting 10 categories...")
            categories = []
            for _ in range(10):
                category_name = fake.word().capitalize()
                categories.append((category_name,))

            insert_category_query = """
                INSERT INTO `category` (category_name) VALUES (%s)
            """
            cursor.executemany(insert_category_query, categories)
            connection.commit()
            category_ids = get_ids(cursor, "category", "category_id")
            print("Inserted 10 categories.")

            ### Step 3: Insert 1000 Good Types ###
            print("Inserting 1000 good types...")
            goodtypes = []
            for _ in range(1000):
                article = random.randint(100000, 999999)
                name = fake.word().capitalize() + " " + fake.word().capitalize()
                category_id = get_random_id(category_ids)
                is_hidden = random.choice(
                    [False, False, False, True]
                )  # Less likely to be hidden
                measure_unit = random.choice(["шт", "кг", "л", "м", "г"])
                has_units = random.randint(0, 1)
                booked_units = 0  # Initially zero
                sell_price = random.randint(100, 10000)
                # Temporary supply_unit_price; actual supply_unit_price will be set in batches
                # To ensure supply_unit_price < sell_price, we'll handle it when creating batches
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

            insert_goodtype_query = """
                INSERT INTO `goodtype`
                (article, name, category_id, is_hidden, measure_unit, has_units, booked_units, sell_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_goodtype_query, goodtypes)
            connection.commit()
            goodtype_ids = get_ids(cursor, "goodtype", "goodtype_id")
            print("Inserted 1000 good types.")

            ### Step 4: Insert 2000 Batches ###
            print("Inserting 2000 batches...")
            batches = []
            for _ in range(2000):
                supplied_at = fake.date_time_between(start_date="-1y", end_date="now")
                updated_at = supplied_at
                goodtype_id = get_random_id(goodtype_ids)

                # Fetch sell_price for this goodtype
                cursor.execute(
                    "SELECT sell_price FROM `goodtype` WHERE goodtype_id = %s",
                    (goodtype_id,),
                )
                sell_price = cursor.fetchone()[0]

                # Ensure supply_unit_price is less than sell_price
                supply_unit_price = random.randint(
                    int(sell_price * 0.5), sell_price - 1
                )
                supply_size = random.randint(10, 1000)
                units_left = supply_size
                batches.append(
                    (
                        supplied_at,
                        updated_at,
                        supply_unit_price,
                        supply_size,
                        units_left,
                        goodtype_id,
                    )
                )

            insert_batch_query = """
                INSERT INTO `batch`
                (supplied_at, updated_at, supply_unit_price, supply_size, units_left, goodtype_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_batch_query, batches)
            connection.commit()
            batch_ids = get_ids(cursor, "batch", "batch_id")
            print("Inserted 2000 batches.")

            ### Step 5: Insert 100 Defect Write-offs ###
            print("Inserting 100 defect write-offs...")
            defect_writeoffs = []
            for _ in range(100):
                while True:
                    batch_id = get_random_id(batch_ids)
                    # Fetch units_left
                    cursor.execute(
                        "SELECT units_left FROM `batch` WHERE batch_id = %s",
                        (batch_id,),
                    )
                    result = cursor.fetchone()
                    if result:
                        units_left = result[0]
                        if units_left > 0:
                            break
                quantity = random.randint(1, min(10, units_left))
                defect_at = fake.date_time_between(start_date="-6m", end_date="now")
                reason = fake.sentence(nb_words=6)
                defect_writeoffs.append((batch_id, quantity, defect_at, reason))

                # Update units_left
                new_units_left = units_left - quantity
                update_batch_query = (
                    "UPDATE `batch` SET units_left = %s WHERE batch_id = %s"
                )
                cursor.execute(update_batch_query, (new_units_left, batch_id))

            insert_defect_writeoff_query = """
                INSERT INTO `defect_writeoff`
                (batch_id, quantity, defect_at, reason)
                VALUES (%s, %s, %s, %s)
            """
            cursor.executemany(insert_defect_writeoff_query, defect_writeoffs)
            connection.commit()
            print("Inserted 100 defect write-offs.")

            ### Step 6: Insert 1000 Orders ###
            print("Inserting 1000 orders...")
            orders = []
            for _ in range(1000):
                customer_id = get_random_id(customer_ids)
                created_at = fake.date_time_between(start_date="-6m", end_date="now")
                updated_at = created_at
                status = "shipped"
                total_price = 0  # Will be updated after inserting order lines
                pay_to_date = fake.date_between(
                    start_date=created_at.date(), end_date="+30d"
                )
                paid_at = None  # Will be set based on status

                paid_at = fake.date_time_between(start_date=created_at, end_date="+1d")

                orders.append(
                    (
                        customer_id,
                        created_at,
                        updated_at,
                        status,
                        total_price,
                        pay_to_date,
                        paid_at,
                    )
                )

            insert_order_query = """
                INSERT INTO `order`
                (customer_id, created_at, updated_at, `status`, total_price, pay_to_date, paid_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_order_query, orders)
            connection.commit()
            order_ids = get_ids(cursor, "order", "order_id")
            print("Inserted 1000 orders.")

            ### Step 7: Insert 2000 Order Lines ###
            print("Inserting 2000 order lines...")
            orderlines = []
            for _ in range(2000):
                order_id = get_random_id(order_ids)
                while True:
                    goodtype_id = get_random_id(goodtype_ids)
                    # Fetch units_left
                    cursor.execute(
                        "SELECT units_left, sell_price FROM `batch` JOIN `goodtype` USING (goodtype_id) WHERE goodtype_id = %s AND units_left > 0",
                        (goodtype_id,),
                    )
                    batches_available = cursor.fetchall()
                    if batches_available:
                        units_available = sum([batch[0] for batch in batches_available])
                        if units_available > 0:
                            break
                if units_available == 0:
                    continue  # Skip if no units available

                quantity = random.randint(1, min(10, units_available))

                # Fetch sell_price from goodtype
                cursor.execute(
                    "SELECT sell_price FROM `goodtype` WHERE goodtype_id = %s",
                    (goodtype_id,),
                )
                sell_price = cursor.fetchone()[0]

                price = sell_price * quantity
                orderlines.append((goodtype_id, order_id, quantity, price))

                # Update units_left in batches (FIFO)
                qty_to_deduct = quantity
                cursor.execute(
                    "SELECT batch_id, units_left FROM `batch` WHERE goodtype_id = %s AND units_left > 0 ORDER BY supplied_at ASC",
                    (goodtype_id,),
                )
                batches = cursor.fetchall()
                for batch in batches:
                    batch_id, units_left = batch
                    if units_left >= qty_to_deduct:
                        new_units = units_left - qty_to_deduct
                        cursor.execute(
                            "UPDATE `batch` SET units_left = %s WHERE batch_id = %s",
                            (new_units, batch_id),
                        )
                        break
                    else:
                        qty_to_deduct -= units_left
                        cursor.execute(
                            "UPDATE `batch` SET units_left = 0 WHERE batch_id = %s",
                            (batch_id,),
                        )
                        if qty_to_deduct == 0:
                            break

            insert_orderline_query = """
                INSERT INTO `orderline`
                (goodtype_id, order_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """
            cursor.executemany(insert_orderline_query, orderlines)
            connection.commit()
            print("Inserted 2000 order lines.")

            ### Step 8: Update Denormalization in Goodtype ###
            print("Updating denormalization in goodtype...")

            cursor.execute(
                """
                UPDATE goodtype AS g SET has_units=COALESCE((SELECT SUM(batch.units_left) FROM batch WHERE batch.goodtype_id=g.goodtype_id),0)
WHERE g.goodtype_id>0;""",
            )
            connection.commit()
            print("Denormalization updated in goodtype.")

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
