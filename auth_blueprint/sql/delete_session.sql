DELETE FROM `session`
WHERE session_id=%s OR valid_until<NOW();
