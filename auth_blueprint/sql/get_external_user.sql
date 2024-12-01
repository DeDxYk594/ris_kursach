-- Получить пользователя по username
SELECT ext_u_id, 'customer', password_hash, username, real_name
FROM `external_user`
WHERE username=%s;
