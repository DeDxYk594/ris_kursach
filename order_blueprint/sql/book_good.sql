UPDATE `goodtype`
SET has_units=has_units-%s, booked_units=booked_units+%s
WHERE goodtype_id=%s;
