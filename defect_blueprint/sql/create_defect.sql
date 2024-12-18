INSERT INTO `defect_writeoff` (goodtype_id, quantity, reason, money)
VALUES (%s, %s, %s, %s*(SELECT sell_price FROM goodtype WHERE goodtype_id=%s));
