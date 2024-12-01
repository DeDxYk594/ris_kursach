SELECT i.int_u_id,
    e.ext_u_id,
    COALESCE(i.role, 'customer'),
    COALESCE(i.password_hash, e.password_hash),
    COALESCE(i.username, e.password_hash),
    COALESCE(i.real_name, e.password_hash)
FROM `session` AS s
JOIN `internal_user` AS i ON s.int_u_id=i.int_u_id
JOIN `internal_user` AS e ON s.ext_u_id=e.ext_u_id
WHERE session_id=%s AND valid_until>NOW();
