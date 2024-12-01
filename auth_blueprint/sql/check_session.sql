SELECT i.int_u_id,
    e.ext_u_id,
    COALESCE(i.role, 'customer'),
    COALESCE(i.password_hash, e.password_hash),
    COALESCE(i.username, e.username),
    COALESCE(i.real_name, e.real_name)
FROM `session` AS s
LEFT JOIN `internal_user` AS i ON s.int_u_id=i.int_u_id
LEFT JOIN `external_user` AS e ON s.ext_u_id=e.ext_u_id
WHERE session_id=%s AND valid_until>NOW();
