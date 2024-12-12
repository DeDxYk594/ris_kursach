SELECT c.name, c.customer_id, c.address, c.phone, c.bik, c.acc_num, c.bank_name, c.contract_date
FROM external_user AS u
JOIN customer AS c USING(customer_id)
WHERE u.ext_u_id=%s;
