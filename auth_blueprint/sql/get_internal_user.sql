-- Получить пользователя по username
SELECT ext_u_id, role, password_hash, username, real_name
FROM `internal_user`
WHERE username=%s;
