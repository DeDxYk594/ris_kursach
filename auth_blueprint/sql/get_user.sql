-- Получить пользователя по username
SELECT u_id, role, password_hash, username, real_name
FROM `user`
WHERE username=%s;
