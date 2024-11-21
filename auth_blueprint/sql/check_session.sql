SELECT u_id
FROM `session`
WHERE session_id=%s AND valid_until>NOW();
