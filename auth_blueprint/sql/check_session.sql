SELECT u.u_id, u.role,
    u.password_hash, u.username, u.real_name
FROM `session` AS s
JOIN `user` AS u USING(u_id)
WHERE session_id=%s AND valid_until>NOW();
